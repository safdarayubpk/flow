"""
Unit tests for Kafka event handlers.

Tests cover:
- Notification handlers: process_task_created, process_reminder_triggered
- Recurring handler: process_recurring_task_created
- User isolation validation (skip events without user_id)
- Malformed event handling (log error and skip)
"""

import pytest
import logging
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from src.services.kafka.handlers import (
    process_task_created,
    process_reminder_triggered,
    process_recurring_task_created,
    _calculate_next_occurrence,
)
from src.services.kafka.events import EventTypes


# =============================================================================
# Notification Handler Tests (US2)
# =============================================================================

class TestProcessTaskCreated:
    """Tests for process_task_created notification handler."""

    @pytest.mark.asyncio
    async def test_logs_notification_for_valid_event(self, caplog):
        """Should log notification with task title and user_id."""
        event = {
            "event_type": EventTypes.TASK_CREATED,
            "user_id": 42,
            "payload": {"task_id": 1, "title": "Buy groceries"},
        }
        with caplog.at_level(logging.INFO):
            await process_task_created(event)
        assert "Buy groceries" in caplog.text
        assert "42" in caplog.text

    @pytest.mark.asyncio
    async def test_skips_event_without_user_id(self, caplog):
        """User isolation: events without user_id must be skipped."""
        event = {
            "event_type": EventTypes.TASK_CREATED,
            "payload": {"task_id": 1, "title": "No user"},
        }
        with caplog.at_level(logging.WARNING):
            await process_task_created(event)
        assert "missing user_id" in caplog.text

    @pytest.mark.asyncio
    async def test_handles_missing_payload(self, caplog):
        """Should handle event with empty/missing payload gracefully."""
        event = {"event_type": EventTypes.TASK_CREATED, "user_id": 1}
        with caplog.at_level(logging.INFO):
            await process_task_created(event)
        assert "Unknown Task" in caplog.text

    @pytest.mark.asyncio
    async def test_handles_missing_title(self, caplog):
        """Should use 'Unknown Task' when title is missing."""
        event = {
            "event_type": EventTypes.TASK_CREATED,
            "user_id": 1,
            "payload": {"task_id": 5},
        }
        with caplog.at_level(logging.INFO):
            await process_task_created(event)
        assert "Unknown Task" in caplog.text


class TestProcessReminderTriggered:
    """Tests for process_reminder_triggered notification handler."""

    @pytest.mark.asyncio
    async def test_logs_reminder_for_valid_event(self, caplog):
        """Should log reminder notification with task info."""
        event = {
            "event_type": EventTypes.REMINDER_TRIGGERED,
            "user_id": 7,
            "payload": {
                "task_id": 3,
                "title": "Doctor appointment",
                "due_date": "2026-02-15T10:00:00",
            },
        }
        with caplog.at_level(logging.INFO):
            await process_reminder_triggered(event)
        assert "Doctor appointment" in caplog.text
        assert "7" in caplog.text

    @pytest.mark.asyncio
    async def test_skips_event_without_user_id(self, caplog):
        """User isolation: events without user_id must be skipped."""
        event = {
            "event_type": EventTypes.REMINDER_TRIGGERED,
            "payload": {"task_id": 3, "title": "No user"},
        }
        with caplog.at_level(logging.WARNING):
            await process_reminder_triggered(event)
        assert "missing user_id" in caplog.text

    @pytest.mark.asyncio
    async def test_handles_missing_due_date(self, caplog):
        """Should work even when due_date is not in the payload."""
        event = {
            "event_type": EventTypes.REMINDER_TRIGGERED,
            "user_id": 1,
            "payload": {"task_id": 3, "title": "No due date"},
        }
        with caplog.at_level(logging.INFO):
            await process_reminder_triggered(event)
        assert "No due date" in caplog.text

    @pytest.mark.asyncio
    async def test_includes_due_date_when_present(self, caplog):
        """Should include due_date in log when present."""
        event = {
            "event_type": EventTypes.REMINDER_TRIGGERED,
            "user_id": 1,
            "payload": {
                "task_id": 3,
                "title": "Task",
                "due_date": "2026-03-01T09:00:00",
            },
        }
        with caplog.at_level(logging.INFO):
            await process_reminder_triggered(event)
        assert "2026-03-01T09:00:00" in caplog.text


# =============================================================================
# Recurring Task Handler Tests (US3)
# =============================================================================

class TestProcessRecurringTaskCreated:
    """Tests for process_recurring_task_created handler."""

    @pytest.mark.asyncio
    async def test_skips_event_without_user_id(self, caplog):
        """User isolation: events without user_id must be skipped."""
        event = {
            "event_type": EventTypes.RECURRING_TASK_CREATED,
            "payload": {"task_id": 1, "title": "Recurring", "recurrence_rule": "DAILY"},
        }
        with caplog.at_level(logging.WARNING):
            await process_recurring_task_created(event)
        assert "missing user_id" in caplog.text

    @pytest.mark.asyncio
    async def test_skips_event_without_recurrence_rule(self, caplog):
        """Should skip if no recurrence_rule in payload."""
        event = {
            "event_type": EventTypes.RECURRING_TASK_CREATED,
            "user_id": 1,
            "payload": {"task_id": 1, "title": "No rule"},
        }
        with caplog.at_level(logging.WARNING):
            await process_recurring_task_created(event)
        assert "No recurrence_rule" in caplog.text

    @pytest.mark.asyncio
    async def test_skips_duplicate_instance(self, caplog):
        """Idempotency: should skip if an instance already exists."""
        event = {
            "event_type": EventTypes.RECURRING_TASK_CREATED,
            "user_id": 1,
            "payload": {"task_id": 10, "title": "Daily standup", "recurrence_rule": "DAILY"},
        }

        mock_existing_task = MagicMock()

        with patch("src.services.kafka.handlers.Session") as MockSession, \
             patch("src.services.kafka.handlers.produce_event", new_callable=AsyncMock):
            mock_session_instance = MagicMock()
            MockSession.return_value.__enter__ = MagicMock(return_value=mock_session_instance)
            MockSession.return_value.__exit__ = MagicMock(return_value=False)
            mock_session_instance.exec.return_value.first.return_value = mock_existing_task

            with caplog.at_level(logging.DEBUG):
                await process_recurring_task_created(event)
            assert "already exists" in caplog.text

    @pytest.mark.asyncio
    async def test_creates_new_instance_when_none_exists(self):
        """Should create new task instance and publish events."""
        event = {
            "event_type": EventTypes.RECURRING_TASK_CREATED,
            "user_id": 1,
            "payload": {"task_id": 10, "title": "Weekly review", "recurrence_rule": "WEEKLY"},
        }

        mock_new_task = MagicMock()
        mock_new_task.id = 99

        # TaskService is imported inside the function, so patch at source
        with patch("src.services.kafka.handlers.Session") as MockSession, \
             patch("src.services.kafka.handlers.produce_event", new_callable=AsyncMock) as mock_produce, \
             patch("src.services.task_service.TaskService") as MockTaskService:
            mock_session_instance = MagicMock()
            MockSession.return_value.__enter__ = MagicMock(return_value=mock_session_instance)
            MockSession.return_value.__exit__ = MagicMock(return_value=False)
            # No existing instance found
            mock_session_instance.exec.return_value.first.return_value = None
            MockTaskService.create_task.return_value = mock_new_task

            await process_recurring_task_created(event)

            # Verify task was created
            MockTaskService.create_task.assert_called_once()
            # Verify recurring-instance-created event was published
            mock_produce.assert_awaited_once()
            call_kwargs = mock_produce.call_args
            assert call_kwargs[1]["event_type"] == EventTypes.RECURRING_INSTANCE_CREATED or \
                   call_kwargs[0][0] == EventTypes.RECURRING_INSTANCE_CREATED


# =============================================================================
# Helper Function Tests
# =============================================================================

class TestCalculateNextOccurrence:
    """Tests for _calculate_next_occurrence helper."""

    def test_daily_recurrence(self):
        """Daily rule should return ~1 day from now."""
        result = _calculate_next_occurrence("DAILY")
        expected = datetime.utcnow() + timedelta(days=1)
        assert abs((result - expected).total_seconds()) < 2

    def test_weekly_recurrence(self):
        """Weekly rule should return ~7 days from now."""
        result = _calculate_next_occurrence("WEEKLY")
        expected = datetime.utcnow() + timedelta(weeks=1)
        assert abs((result - expected).total_seconds()) < 2

    def test_monthly_recurrence(self):
        """Monthly rule should return ~30 days from now."""
        result = _calculate_next_occurrence("MONTHLY")
        expected = datetime.utcnow() + timedelta(days=30)
        assert abs((result - expected).total_seconds()) < 2

    def test_yearly_recurrence(self):
        """Yearly rule should return ~365 days from now."""
        result = _calculate_next_occurrence("YEARLY")
        expected = datetime.utcnow() + timedelta(days=365)
        assert abs((result - expected).total_seconds()) < 2

    def test_default_is_daily(self):
        """Unknown rule should default to daily."""
        result = _calculate_next_occurrence("UNKNOWN_RULE")
        expected = datetime.utcnow() + timedelta(days=1)
        assert abs((result - expected).total_seconds()) < 2

    def test_case_insensitive(self):
        """Rules should be case-insensitive."""
        result_lower = _calculate_next_occurrence("daily")
        result_upper = _calculate_next_occurrence("DAILY")
        assert abs((result_lower - result_upper).total_seconds()) < 2

    def test_rrule_format_daily(self):
        """RRULE format with INTERVAL=1 should map to daily."""
        result = _calculate_next_occurrence("RRULE:FREQ=DAILY;INTERVAL=1")
        expected = datetime.utcnow() + timedelta(days=1)
        assert abs((result - expected).total_seconds()) < 2


# =============================================================================
# Consumer _process_message Tests (event routing & validation)
# =============================================================================

class TestConsumerProcessMessage:
    """Tests for KafkaEventConsumer._process_message event routing."""

    @pytest.mark.asyncio
    async def test_routes_event_to_correct_handler(self):
        """Events should be routed to the registered handler."""
        from src.services.kafka.consumer import KafkaEventConsumer
        handler = AsyncMock()
        consumer = KafkaEventConsumer(topic="test", group_id="test-group")
        consumer.register_handler("task-created", handler)

        event = {"event_type": "task-created", "user_id": 1, "payload": {}}
        await consumer._process_message(event)
        handler.assert_awaited_once_with(event)

    @pytest.mark.asyncio
    async def test_skips_event_without_event_type(self, caplog):
        """Events missing event_type should be skipped."""
        from src.services.kafka.consumer import KafkaEventConsumer
        consumer = KafkaEventConsumer(topic="test", group_id="test-group")

        with caplog.at_level(logging.WARNING):
            await consumer._process_message({"user_id": 1, "payload": {}})
        assert "missing event_type" in caplog.text

    @pytest.mark.asyncio
    async def test_skips_event_without_user_id(self, caplog):
        """User isolation: events without user_id should be skipped."""
        from src.services.kafka.consumer import KafkaEventConsumer
        consumer = KafkaEventConsumer(topic="test", group_id="test-group")

        with caplog.at_level(logging.WARNING):
            await consumer._process_message({"event_type": "task-created", "payload": {}})
        assert "missing user_id" in caplog.text

    @pytest.mark.asyncio
    async def test_ignores_unregistered_event_type(self, caplog):
        """Events with no registered handler should be logged at debug level."""
        from src.services.kafka.consumer import KafkaEventConsumer
        consumer = KafkaEventConsumer(topic="test", group_id="test-group")

        with caplog.at_level(logging.DEBUG):
            await consumer._process_message(
                {"event_type": "unknown-event", "user_id": 1, "payload": {}}
            )
        assert "No handler" in caplog.text


# =============================================================================
# Event Model Tests
# =============================================================================

class TestEventModels:
    """Tests for Pydantic event payload models."""

    def test_task_created_payload(self):
        """TaskCreatedPayload should validate correctly."""
        from src.services.kafka.events import TaskCreatedPayload
        payload = TaskCreatedPayload(task_id=1, title="Test")
        assert payload.task_id == 1
        assert payload.title == "Test"
        assert payload.tags == []
        assert payload.priority is None

    def test_task_updated_payload(self):
        """TaskUpdatedPayload should accept changes dict."""
        from src.services.kafka.events import TaskUpdatedPayload
        payload = TaskUpdatedPayload(task_id=1, changes={"title": "New Title"})
        assert payload.changes["title"] == "New Title"

    def test_task_completed_payload(self):
        """TaskCompletedPayload requires only task_id."""
        from src.services.kafka.events import TaskCompletedPayload
        payload = TaskCompletedPayload(task_id=5)
        assert payload.task_id == 5

    def test_task_deleted_payload(self):
        """TaskDeletedPayload requires only task_id."""
        from src.services.kafka.events import TaskDeletedPayload
        payload = TaskDeletedPayload(task_id=3)
        assert payload.task_id == 3

    def test_reminder_triggered_payload(self):
        """ReminderTriggeredPayload should include title and optional due_date."""
        from src.services.kafka.events import ReminderTriggeredPayload
        payload = ReminderTriggeredPayload(task_id=2, title="Reminder")
        assert payload.title == "Reminder"
        assert payload.due_date is None

    def test_recurring_task_created_payload(self):
        """RecurringTaskCreatedPayload should include recurrence_rule."""
        from src.services.kafka.events import RecurringTaskCreatedPayload
        payload = RecurringTaskCreatedPayload(
            task_id=1, title="Daily", recurrence_rule="DAILY"
        )
        assert payload.recurrence_rule == "DAILY"

    def test_recurring_instance_created_payload(self):
        """RecurringInstanceCreatedPayload should include parent_task_id."""
        from src.services.kafka.events import RecurringInstanceCreatedPayload
        payload = RecurringInstanceCreatedPayload(
            task_id=2, parent_task_id=1, title="Instance",
            scheduled_date=datetime(2026, 3, 1)
        )
        assert payload.parent_task_id == 1
