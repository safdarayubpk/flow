'use client';

import React, { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
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
      setFormData({
        ...formData,
        tags: [...formData.tags, newTag.trim()],
      });
      setNewTag('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove),
    }));
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  const handleDueDateChange = (date: Date | undefined) => {
    if (date && selectedTime) {
      // Combine the selected date with the selected time
      const timeParts = selectedTime.split(':');
      const hours = parseInt(timeParts[0]);
      const minutes = parseInt(timeParts[1]);

      date.setHours(hours);
      date.setMinutes(minutes);

      setFormData(prev => ({
        ...prev,
        due_date: date.toISOString(),
      }));
    } else if (date) {
      // If no time is selected, use default time
      setFormData(prev => ({
        ...prev,
        due_date: date.toISOString(),
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        due_date: undefined,
      }));
    }
  };

  const handleTimeChange = (time: string) => {
    setSelectedTime(time);
    if (formData.due_date) {
      // Update the time part of the existing due date
      const date = new Date(formData.due_date);
      const timeParts = time.split(':');
      const hours = parseInt(timeParts[0]);
      const minutes = parseInt(timeParts[1]);

      date.setHours(hours);
      date.setMinutes(minutes);

      setFormData(prev => ({
        ...prev,
        due_date: date.toISOString(),
      }));
    }
  };

  const handleRecurrenceChange = (enabled: boolean, rule?: string) => {
    setFormData(prev => ({
      ...prev,
      recurrence_rule: enabled ? rule || 'FREQ=DAILY' : undefined,
    }));
  };

  const handleReminderToggle = (checked: boolean) => {
    setFormData(prev => ({
      ...prev,
      reminder_enabled: checked,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Title */}
      <div className="space-y-2">
        <Label htmlFor="title">Title *</Label>
        <Input
          id="title"
          value={formData.title}
          onChange={(e) => setFormData(prev => ({...prev, title: e.target.value}))}
          placeholder="Task title"
          required
        />
      </div>

      {/* Description */}
      <div className="space-y-2">
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData(prev => ({...prev, description: e.target.value}))}
          placeholder="Task description"
        />
      </div>

      {/* Priority */}
      <div className="space-y-2">
        <Label>Priority</Label>
        <div className="flex space-x-2">
          {(['high', 'medium', 'low'] as const).map(level => (
            <button
              key={level}
              type="button"
              className={`px-3 py-1 rounded-md text-sm ${
                formData.priority === level
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
              onClick={() => setFormData(prev => ({
                ...prev,
                priority: prev.priority === level ? null : level
              }))}
            >
              {level.charAt(0).toUpperCase() + level.slice(1)}
            </button>
          ))}
        </div>
        {formData.priority && <PriorityBadge priority={formData.priority} className="mt-2" />}
      </div>

      {/* Tags */}
      <div className="space-y-2">
        <Label>Tags</Label>
        <div className="flex space-x-2">
          <Input
            value={newTag}
            onChange={(e) => setNewTag(e.target.value)}
            placeholder="Add a tag"
            onKeyDown={handleKeyPress}
          />
          <Button type="button" onClick={handleAddTag}>Add</Button>
        </div>
        <TagChips tags={formData.tags} onRemove={handleRemoveTag} className="mt-2" />
      </div>

      {/* Due Date */}
      <div className="space-y-2">
        <Label>Due Date</Label>
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
      <div className="space-y-2">
        <Label>Recurring Task</Label>
        <RecurringToggle
          enabled={!!formData.recurrence_rule}
          onToggle={handleRecurrenceChange}
          initialRule={formData.recurrence_rule}
        />
      </div>

      {/* Reminder */}
      <div className="flex items-center space-x-2 pt-2">
        <Checkbox
          id="reminder-enabled"
          checked={formData.reminder_enabled}
          onCheckedChange={handleReminderToggle}
        />
        <Label htmlFor="reminder-enabled">Enable Reminder</Label>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-2 pt-4">
        <Button type="submit">{submitLabel}</Button>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
};

export default TaskForm;