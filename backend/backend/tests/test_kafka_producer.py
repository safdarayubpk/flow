"""
Unit tests for Kafka producer module.

Tests cover:
- Singleton producer pattern
- Fire-and-forget event publishing
- Graceful degradation when Kafka unavailable
- Event envelope structure
- User isolation (user_id always present)
"""

import json
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# We test the module functions directly by mocking aiokafka
from src.services.kafka.producer import produce_event, get_producer, close_producer
from src.services.kafka.events import EventTypes


@pytest.fixture(autouse=True)
def reset_producer_singleton():
    """Reset the singleton producer before and after each test."""
    import src.services.kafka.producer as prod_module
    prod_module._producer = None
    yield
    prod_module._producer = None


class TestGetProducer:
    """Tests for get_producer() singleton factory."""

    @pytest.mark.asyncio
    async def test_returns_none_when_bootstrap_servers_not_set(self):
        """When KAFKA_BOOTSTRAP_SERVERS is empty/None, producer is disabled."""
        with patch("src.services.kafka.producer.settings") as mock_settings:
            mock_settings.kafka_bootstrap_servers = None
            result = await get_producer()
            assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_when_bootstrap_servers_empty(self):
        """Empty string should also disable producer."""
        with patch("src.services.kafka.producer.settings") as mock_settings:
            mock_settings.kafka_bootstrap_servers = ""
            result = await get_producer()
            assert result is None

    @pytest.mark.asyncio
    async def test_creates_producer_when_configured(self):
        """When bootstrap servers set, producer should be created and started."""
        mock_producer = AsyncMock()
        with patch("src.services.kafka.producer.settings") as mock_settings, \
             patch("src.services.kafka.producer.AIOKafkaProducer", return_value=mock_producer):
            mock_settings.kafka_bootstrap_servers = "localhost:9092"
            result = await get_producer()
            assert result is mock_producer
            mock_producer.start.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_singleton_returns_same_instance(self):
        """Subsequent calls should return the same producer instance."""
        mock_producer = AsyncMock()
        with patch("src.services.kafka.producer.settings") as mock_settings, \
             patch("src.services.kafka.producer.AIOKafkaProducer", return_value=mock_producer):
            mock_settings.kafka_bootstrap_servers = "localhost:9092"
            first = await get_producer()
            second = await get_producer()
            assert first is second
            # start() should only be called once
            mock_producer.start.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_returns_none_on_connection_failure(self):
        """If Kafka connection fails, should return None (graceful degradation)."""
        mock_producer = AsyncMock()
        mock_producer.start.side_effect = Exception("Connection refused")
        with patch("src.services.kafka.producer.settings") as mock_settings, \
             patch("src.services.kafka.producer.AIOKafkaProducer", return_value=mock_producer):
            mock_settings.kafka_bootstrap_servers = "localhost:9092"
            result = await get_producer()
            assert result is None


class TestCloseProducer:
    """Tests for close_producer() shutdown."""

    @pytest.mark.asyncio
    async def test_close_stops_producer(self):
        """close_producer should stop the running producer."""
        import src.services.kafka.producer as prod_module
        mock_producer = AsyncMock()
        prod_module._producer = mock_producer

        await close_producer()
        mock_producer.stop.assert_awaited_once()
        assert prod_module._producer is None

    @pytest.mark.asyncio
    async def test_close_noop_when_no_producer(self):
        """close_producer should not crash when no producer exists."""
        await close_producer()  # Should not raise

    @pytest.mark.asyncio
    async def test_close_handles_stop_error(self):
        """close_producer should handle errors during stop."""
        import src.services.kafka.producer as prod_module
        mock_producer = AsyncMock()
        mock_producer.stop.side_effect = Exception("Stop failed")
        prod_module._producer = mock_producer

        await close_producer()  # Should not raise
        assert prod_module._producer is None


class TestProduceEvent:
    """Tests for produce_event() fire-and-forget publishing."""

    @pytest.mark.asyncio
    async def test_returns_false_when_producer_disabled(self):
        """When Kafka is disabled, produce_event returns False without crashing."""
        with patch("src.services.kafka.producer.get_producer", new_callable=AsyncMock, return_value=None):
            result = await produce_event("task-created", user_id=1, payload={"task_id": 1})
            assert result is False

    @pytest.mark.asyncio
    async def test_publishes_event_successfully(self):
        """Event should be sent via send_and_wait with correct structure."""
        mock_producer = AsyncMock()
        with patch("src.services.kafka.producer.get_producer", new_callable=AsyncMock, return_value=mock_producer), \
             patch("src.services.kafka.producer.settings") as mock_settings:
            mock_settings.kafka_topic = "todo-events"

            result = await produce_event(
                event_type="task-created",
                user_id=42,
                payload={"task_id": 1, "title": "Test Task"}
            )

            assert result is True
            mock_producer.send_and_wait.assert_awaited_once()

            # Verify event envelope structure
            call_args = mock_producer.send_and_wait.call_args
            topic = call_args[0][0]
            event = call_args[0][1]

            assert topic == "todo-events"
            assert event["event_type"] == "task-created"
            assert event["user_id"] == 42
            assert event["payload"]["task_id"] == 1
            assert event["payload"]["title"] == "Test Task"
            assert "timestamp" in event

    @pytest.mark.asyncio
    async def test_event_envelope_has_required_fields(self):
        """Every event must have event_type, timestamp, user_id, payload."""
        mock_producer = AsyncMock()
        with patch("src.services.kafka.producer.get_producer", new_callable=AsyncMock, return_value=mock_producer), \
             patch("src.services.kafka.producer.settings") as mock_settings:
            mock_settings.kafka_topic = "todo-events"

            await produce_event(
                event_type=EventTypes.TASK_COMPLETED,
                user_id=99,
                payload={"task_id": 5}
            )

            event = mock_producer.send_and_wait.call_args[0][1]
            required_keys = {"event_type", "timestamp", "user_id", "payload"}
            assert required_keys.issubset(event.keys())

    @pytest.mark.asyncio
    async def test_uses_custom_topic(self):
        """When topic is explicitly provided, it should be used."""
        mock_producer = AsyncMock()
        with patch("src.services.kafka.producer.get_producer", new_callable=AsyncMock, return_value=mock_producer):
            await produce_event(
                event_type="task-created",
                user_id=1,
                payload={},
                topic="custom-topic"
            )

            topic = mock_producer.send_and_wait.call_args[0][0]
            assert topic == "custom-topic"

    @pytest.mark.asyncio
    async def test_fire_and_forget_on_send_failure(self):
        """If send fails, produce_event returns False but does NOT raise."""
        mock_producer = AsyncMock()
        mock_producer.send_and_wait.side_effect = Exception("Broker unavailable")
        with patch("src.services.kafka.producer.get_producer", new_callable=AsyncMock, return_value=mock_producer):
            result = await produce_event(
                event_type="task-created",
                user_id=1,
                payload={"task_id": 1}
            )
            assert result is False

    @pytest.mark.asyncio
    async def test_user_id_always_in_event(self):
        """User isolation: user_id must always be present in event envelope."""
        mock_producer = AsyncMock()
        with patch("src.services.kafka.producer.get_producer", new_callable=AsyncMock, return_value=mock_producer), \
             patch("src.services.kafka.producer.settings") as mock_settings:
            mock_settings.kafka_topic = "todo-events"

            for event_type in [EventTypes.TASK_CREATED, EventTypes.TASK_UPDATED,
                               EventTypes.TASK_COMPLETED, EventTypes.TASK_DELETED]:
                await produce_event(event_type=event_type, user_id=7, payload={})
                event = mock_producer.send_and_wait.call_args[0][1]
                assert event["user_id"] == 7, f"user_id missing from {event_type} event"

    @pytest.mark.asyncio
    async def test_timestamp_is_iso_format(self):
        """Timestamp should be ISO 8601 UTC format."""
        from datetime import datetime
        mock_producer = AsyncMock()
        with patch("src.services.kafka.producer.get_producer", new_callable=AsyncMock, return_value=mock_producer), \
             patch("src.services.kafka.producer.settings") as mock_settings:
            mock_settings.kafka_topic = "todo-events"

            await produce_event(event_type="task-created", user_id=1, payload={})
            event = mock_producer.send_and_wait.call_args[0][1]
            # Should be parseable as ISO datetime
            datetime.fromisoformat(event["timestamp"])


class TestEventTypes:
    """Tests for event type constants."""

    def test_all_event_types_defined(self):
        """All required event types should be defined."""
        assert EventTypes.TASK_CREATED == "task-created"
        assert EventTypes.TASK_UPDATED == "task-updated"
        assert EventTypes.TASK_COMPLETED == "task-completed"
        assert EventTypes.TASK_DELETED == "task-deleted"
        assert EventTypes.REMINDER_TRIGGERED == "reminder-triggered"
        assert EventTypes.RECURRING_TASK_CREATED == "recurring-task-created"
        assert EventTypes.RECURRING_INSTANCE_CREATED == "recurring-instance-created"

    def test_at_least_three_event_types(self):
        """SC-002: At least 3 event types must be implemented."""
        event_types = [
            EventTypes.TASK_CREATED,
            EventTypes.TASK_UPDATED,
            EventTypes.TASK_COMPLETED,
            EventTypes.TASK_DELETED,
            EventTypes.REMINDER_TRIGGERED,
            EventTypes.RECURRING_TASK_CREATED,
            EventTypes.RECURRING_INSTANCE_CREATED,
        ]
        assert len(event_types) >= 3
