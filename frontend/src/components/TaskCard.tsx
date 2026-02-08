'use client';

import React from 'react';
import PriorityBadge from './PriorityBadge';
import TagChips from './TagChips';

interface Task {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
  user_id: string;
  priority?: 'high' | 'medium' | 'low' | null;
  tags?: string[];
  due_date?: string;
  recurrence_rule?: string;
  reminder_enabled: boolean;
}

interface TaskCardProps {
  task: Task;
  onToggle: (id: number) => void;
  onEdit: (id: number) => void;
  onDelete: (id: number) => void;
  className?: string;
}

const TaskCard: React.FC<TaskCardProps> = ({
  task,
  onToggle,
  onEdit,
  onDelete,
  className = ''
}) => {
  const formatDate = (dateString: string) => {
    // Ensure the date string is treated as UTC if no timezone specified
    // Backend may return "2026-02-06T06:00:00" without Z suffix
    let normalizedDateString = dateString;
    if (!dateString.endsWith('Z') && !dateString.includes('+') && !dateString.includes('-', 10)) {
      normalizedDateString = dateString + 'Z';
    }
    const date = new Date(normalizedDateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className={`group flex flex-col p-3 sm:p-4 mb-3 bg-white shadow rounded-lg border border-gray-200 hover:shadow-md transition-shadow ${className}`}>
      <div className="flex flex-col sm:flex-row sm:items-start gap-2 sm:gap-3">
        <div className="flex items-start gap-2 sm:gap-3 flex-1 min-w-0">
          <input
            type="checkbox"
            checked={task.completed}
            onChange={() => onToggle(task.id)}
            className="mt-1 h-5 w-5 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 flex-shrink-0"
            aria-label={`Mark task ${task.title} as ${task.completed ? 'incomplete' : 'complete'}`}
          />

          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-1">
              <h3 className={`text-base sm:text-lg font-medium truncate ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                {task.title}
              </h3>
              {task.priority && <PriorityBadge priority={task.priority} />}
            </div>

            {task.description && (
              <p className={`text-sm mb-2 break-words ${task.completed ? 'text-gray-400' : 'text-gray-600'}`}>
                {task.description}
              </p>
            )}

            {task.tags && task.tags.length > 0 && (
              <TagChips tags={task.tags} className="mb-2" />
            )}

            {(task.due_date || task.recurrence_rule || task.reminder_enabled) && (
              <div className="flex flex-wrap gap-2 text-xs text-gray-500 mt-1">
                {task.due_date && (
                  <span>Due: {formatDate(task.due_date)}</span>
                )}
                {task.recurrence_rule && (
                  <span>Recurring</span>
                )}
                {task.reminder_enabled && (
                  <span>Reminder</span>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="flex flex-row gap-2 ml-7 sm:ml-0 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity duration-150">
          <button
            onClick={() => onEdit(task.id)}
            className="inline-flex items-center justify-center px-3 py-2 sm:py-1.5 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 min-h-[44px] sm:min-h-0"
          >
            Edit
          </button>
          <button
            onClick={() => onDelete(task.id)}
            className="inline-flex items-center justify-center px-3 py-2 sm:py-1.5 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 min-h-[44px] sm:min-h-0"
          >
            Delete
          </button>
        </div>
      </div>
      <div className="mt-2 text-xs text-gray-500 ml-7 sm:ml-0">
        {new Date(task.created_at).toLocaleDateString()}
      </div>
    </div>
  );
};

export default TaskCard;
