'use client';

import React, { useState } from 'react';
import PriorityBadge from '@/components/PriorityBadge';
import TagChips from '@/components/TagChips';
import DatePicker from '@/components/DatePicker';
import TimePicker from '@/components/TimePicker';
import RecurringToggle from '@/components/RecurringToggle';

interface TaskFormData {
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low' | null;
  tags: string[];
  due_date?: string;
  recurrence_rule?: string;
  reminder_enabled: boolean;
}

interface TaskFormProps {
  initialData?: Partial<TaskFormData>;
  onSubmit: (data: TaskFormData) => void;
  onCancel?: () => void;
  submitLabel?: string;
}

const TaskForm: React.FC<TaskFormProps> = ({
  initialData = {},
  onSubmit,
  onCancel,
  submitLabel = 'Create Task'
}) => {
  const [formData, setFormData] = useState<TaskFormData>({
    title: initialData.title || '',
    description: initialData.description || '',
    priority: initialData.priority || null,
    tags: initialData.tags || [],
    due_date: initialData.due_date || undefined,
    recurrence_rule: initialData.recurrence_rule || undefined,
    reminder_enabled: initialData.reminder_enabled ?? false,
  });

  const [newTag, setNewTag] = useState('');
  const [selectedTime, setSelectedTime] = useState<string>(
    initialData.due_date ? new Date(initialData.due_date).toTimeString().substring(0, 5) : '09:00'
  );

  const handleAddTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      setFormData(prev => ({ ...prev, tags: [...prev.tags, newTag.trim()] }));
      setNewTag('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData(prev => ({ ...prev, tags: prev.tags.filter(tag => tag !== tagToRemove) }));
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  const handleDueDateChange = (date: Date | undefined) => {
    if (date && selectedTime) {
      const [hours, minutes] = selectedTime.split(':').map(Number);
      date.setHours(hours);
      date.setMinutes(minutes);
      setFormData(prev => ({ ...prev, due_date: date.toISOString() }));
    } else if (date) {
      setFormData(prev => ({ ...prev, due_date: date.toISOString() }));
    } else {
      setFormData(prev => ({ ...prev, due_date: undefined }));
    }
  };

  const handleTimeChange = (time: string) => {
    setSelectedTime(time);
    if (formData.due_date) {
      const date = new Date(formData.due_date);
      const [hours, minutes] = time.split(':').map(Number);
      date.setHours(hours);
      date.setMinutes(minutes);
      setFormData(prev => ({ ...prev, due_date: date.toISOString() }));
    }
  };

  const handleRecurrenceChange = (enabled: boolean, rule?: string) => {
    setFormData(prev => ({ ...prev, recurrence_rule: enabled ? rule || 'FREQ=DAILY' : undefined }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 bg-white border rounded-lg shadow-sm mb-4">
      {/* Title */}
      <div className="space-y-1">
        <label htmlFor="title" className="block text-sm font-medium text-gray-700">Title *</label>
        <input
          id="title"
          value={formData.title}
          onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
          placeholder="Task title"
          required
          className="w-full rounded-md border border-gray-300 py-2 px-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none"
        />
      </div>

      {/* Description */}
      <div className="space-y-1">
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">Description</label>
        <textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
          placeholder="Task description"
          rows={3}
          className="w-full rounded-md border border-gray-300 py-2 px-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none resize-y"
        />
      </div>

      {/* Priority */}
      <div className="space-y-1">
        <span className="block text-sm font-medium text-gray-700">Priority</span>
        <div className="flex space-x-2">
          {(['high', 'medium', 'low'] as const).map(level => (
            <button
              key={level}
              type="button"
              className={`px-3 py-1 rounded-md text-sm ${
                formData.priority === level
                  ? 'bg-indigo-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
              onClick={() => setFormData(prev => ({ ...prev, priority: prev.priority === level ? null : level }))}
            >
              {level.charAt(0).toUpperCase() + level.slice(1)}
            </button>
          ))}
        </div>
        {formData.priority && <PriorityBadge priority={formData.priority} className="mt-2" />}
      </div>

      {/* Tags */}
      <div className="space-y-1">
        <span className="block text-sm font-medium text-gray-700">Tags</span>
        <div className="flex space-x-2">
          <input
            value={newTag}
            onChange={(e) => setNewTag(e.target.value)}
            placeholder="Add a tag"
            onKeyDown={handleKeyPress}
            className="flex-1 rounded-md border border-gray-300 py-2 px-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none"
          />
          <button
            type="button"
            onClick={handleAddTag}
            className="px-4 py-2 text-sm font-medium rounded-md bg-indigo-600 text-white hover:bg-indigo-700"
          >
            Add
          </button>
        </div>
        <TagChips tags={formData.tags} onRemove={handleRemoveTag} className="mt-2" />
      </div>

      {/* Due Date */}
      <div className="space-y-1">
        <span className="block text-sm font-medium text-gray-700">Due Date</span>
        <div className="flex flex-col sm:flex-row gap-2">
          <DatePicker
            date={formData.due_date ? new Date(formData.due_date) : undefined}
            onDateChange={handleDueDateChange}
            placeholder="Select due date"
          />
          <TimePicker
            time={selectedTime}
            onTimeChange={handleTimeChange}
          />
        </div>
      </div>

      {/* Recurring Task */}
      <div className="space-y-1">
        <span className="block text-sm font-medium text-gray-700">Recurring Task</span>
        <RecurringToggle
          enabled={!!formData.recurrence_rule}
          onToggle={handleRecurrenceChange}
          initialRule={formData.recurrence_rule}
        />
      </div>

      {/* Reminder */}
      <label className="flex items-center space-x-2 pt-2 cursor-pointer">
        <input
          type="checkbox"
          checked={formData.reminder_enabled}
          onChange={(e) => setFormData(prev => ({ ...prev, reminder_enabled: e.target.checked }))}
          className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
        />
        <span className="text-sm font-medium text-gray-700">Enable Reminder</span>
      </label>

      {/* Action Buttons */}
      <div className="flex space-x-2 pt-4">
        <button
          type="submit"
          className="px-4 py-2 text-sm font-medium rounded-md bg-indigo-600 text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          {submitLabel}
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
};

export default TaskForm;
