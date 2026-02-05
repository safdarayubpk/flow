import React from 'react';

// Define the Task type
type Task = {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
  user_id: string;
};

interface TaskCardProps {
  task: Task;
  onToggle: (id: number) => void;
  onDelete: (id: number) => void;
  onEdit: (id: number) => void;
}

export default function TaskCard({ task, onToggle, onDelete, onEdit }: TaskCardProps) {
  const { id, title, description, completed } = task;

  return (
    <div className="flex flex-col p-3 sm:p-4 mb-3 bg-white shadow rounded-lg border border-gray-200">
      <div className="flex flex-col sm:flex-row sm:items-start gap-2 sm:gap-3">
        <div className="flex items-start gap-2 sm:gap-3 flex-1 min-w-0">
          <input
            type="checkbox"
            checked={completed}
            onChange={() => onToggle(id)}
            className="mt-1 h-5 w-5 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 flex-shrink-0"
          />
          <div className="flex-1 min-w-0">
            <h3 className={`text-base sm:text-lg font-medium ${completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
              {title}
            </h3>
            {description && (
              <div className="mt-1 text-sm text-gray-500 break-words">
                {description}
              </div>
            )}
          </div>
        </div>
        <div className="flex flex-row sm:flex-row gap-2 ml-7 sm:ml-0">
          <button
            onClick={() => onEdit(id)}
            className="inline-flex items-center justify-center px-3 py-2 sm:py-1.5 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 min-h-[44px] sm:min-h-0"
          >
            Edit
          </button>
          <button
            onClick={() => onDelete(id)}
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
}