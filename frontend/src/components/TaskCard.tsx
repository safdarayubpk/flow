'use client';

import React from 'react';
import { Card, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
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
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Card className={`w-full ${className}`}>
      <CardContent className="p-4">
        <div className="flex items-start space-x-3">
          <Checkbox
            checked={task.completed}
            onCheckedChange={() => onToggle(task.id)}
            aria-label={`Mark task ${task.title} as ${task.completed ? 'incomplete' : 'complete'}`}
          />

          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-1">
              <h3 className={`font-medium truncate ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                {task.title}
              </h3>
              {task.priority && <PriorityBadge priority={task.priority} />}
            </div>

            {task.description && (
              <p className={`text-sm mb-2 ${task.completed ? 'text-gray-400' : 'text-gray-600'}`}>
                {task.description}
              </p>
            )}

            {task.tags && task.tags.length > 0 && (
              <TagChips tags={task.tags} className="mb-2" />
            )}

            {(task.due_date || task.recurrence_rule || task.reminder_enabled) && (
              <div className="flex flex-wrap gap-2 text-xs text-gray-500 mt-1">
                {task.due_date && (
                  <div className="flex items-center">
                    <span>📅 Due: {formatDate(task.due_date)}</span>
                  </div>
                )}
                {task.recurrence_rule && (
                  <div className="flex items-center">
                    <span>🔄 Recurring</span>
                  </div>
                )}
                {task.reminder_enabled && (
                  <div className="flex items-center">
                    <span>🔔 Reminder</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </CardContent>

      <CardFooter className="flex justify-between p-4 border-t">
        <Button variant="outline" size="sm" onClick={() => onEdit(task.id)}>
          Edit
        </Button>
        <Button variant="destructive" size="sm" onClick={() => onDelete(task.id)}>
          Delete
        </Button>
      </CardFooter>
    </Card>
  );
};

export default TaskCard;