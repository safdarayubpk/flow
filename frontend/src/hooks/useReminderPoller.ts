'use client';

import { useEffect, useRef, useCallback } from 'react';
import { apiCall } from '@/lib/auth';
import NotificationService from '@/services/notificationService';

interface Task {
  id: number;
  title: string;
  description?: string;
  due_date?: string;
  reminder_enabled: boolean;
  completed: boolean;
}

const POLL_INTERVAL_MS = 30000; // Poll every 30 seconds
const REMINDER_WINDOW_MS = 60000; // Notify if due within 1 minute
const NOTIFIED_TASKS_KEY = 'notified_reminder_tasks';

/**
 * Hook that polls for tasks with reminders and shows browser notifications
 * when tasks are due within the reminder window.
 */
export function useReminderPoller(enabled: boolean = true) {
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Get already-notified task IDs from localStorage
  const getNotifiedTasks = useCallback((): Set<number> => {
    if (typeof window === 'undefined') return new Set();
    try {
      const stored = localStorage.getItem(NOTIFIED_TASKS_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        // Clean up old entries (older than 24 hours)
        const now = Date.now();
        const filtered = Object.entries(parsed)
          .filter(([, timestamp]) => now - (timestamp as number) < 86400000)
          .reduce((acc, [id, ts]) => ({ ...acc, [id]: ts }), {});
        localStorage.setItem(NOTIFIED_TASKS_KEY, JSON.stringify(filtered));
        return new Set(Object.keys(filtered).map(Number));
      }
    } catch (e) {
      console.error('Error reading notified tasks:', e);
    }
    return new Set();
  }, []);

  // Mark a task as notified
  const markTaskNotified = useCallback((taskId: number) => {
    if (typeof window === 'undefined') return;
    try {
      const stored = localStorage.getItem(NOTIFIED_TASKS_KEY);
      const parsed = stored ? JSON.parse(stored) : {};
      parsed[taskId] = Date.now();
      localStorage.setItem(NOTIFIED_TASKS_KEY, JSON.stringify(parsed));
    } catch (e) {
      console.error('Error saving notified task:', e);
    }
  }, []);

  // Check tasks and show notifications for due reminders
  const checkReminders = useCallback(async () => {
    try {
      const response = await apiCall('/api/v1/tasks', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) return;

      const tasks: Task[] = await response.json();
      const notifiedTasks = getNotifiedTasks();
      const now = Date.now();

      for (const task of tasks) {
        // Skip if already notified, no reminder, completed, or no due date
        if (
          notifiedTasks.has(task.id) ||
          !task.reminder_enabled ||
          task.completed ||
          !task.due_date
        ) {
          continue;
        }

        const dueTime = new Date(task.due_date).getTime();
        const timeUntilDue = dueTime - now;

        // Notify if due within the reminder window (1 minute) or just passed (within 5 min)
        if (timeUntilDue <= REMINDER_WINDOW_MS && timeUntilDue > -300000) {
          const isOverdue = timeUntilDue < 0;
          const minutesUntil = Math.ceil(timeUntilDue / 60000);

          NotificationService.showNotification({
            title: isOverdue ? '⏰ Task Overdue!' : '⏰ Task Reminder',
            body: isOverdue
              ? `"${task.title}" is overdue!`
              : `"${task.title}" is due ${minutesUntil <= 0 ? 'now' : `in ${minutesUntil} minute(s)`}`,
            tag: `task-reminder-${task.id}`,
            requireInteraction: true,
          });

          markTaskNotified(task.id);
        }
      }
    } catch (error) {
      console.error('Error checking reminders:', error);
    }
  }, [getNotifiedTasks, markTaskNotified]);

  useEffect(() => {
    if (!enabled) return;

    // Check immediately on mount
    checkReminders();

    // Then poll at regular intervals
    intervalRef.current = setInterval(checkReminders, POLL_INTERVAL_MS);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [enabled, checkReminders]);

  return { checkReminders };
}
