---
name: nextjs-todo-advanced-ui
description: NextJS todo advanced UI, priority badge, tag chips, due date picker, recurring toggle, sort dropdown. Use Tailwind + shadcn/ui for new components with priority badges, colored tag chips, date pickers, toggles, and sort dropdowns. Includes loading/error states, responsive design, and accessibility. Use when implementing advanced UI features for todo applications.
---

# NextJS Todo Advanced UI

## Overview

This skill provides guidance for implementing advanced UI components for NextJS todo applications using Tailwind CSS and shadcn/ui. It covers the implementation of priority badges, tag chips, due date pickers, recurring toggles, and sort dropdowns while maintaining responsive design and accessibility.

## Component Specifications

### Priority Badge Component

Priority badges with color-coded indicators for different priority levels:

```tsx
// components/PriorityBadge.tsx
import React from 'react';

type Priority = 'high' | 'medium' | 'low' | null;

interface PriorityBadgeProps {
  priority: Priority;
  className?: string;
}

const PriorityBadge: React.FC<PriorityBadgeProps> = ({ priority, className = '' }) => {
  if (!priority) return null;

  const priorityStyles = {
    high: 'bg-red-500 text-white',
    medium: 'bg-orange-500 text-white',
    low: 'bg-yellow-500 text-gray-900',
  };

  const priorityLabels = {
    high: 'High',
    medium: 'Medium',
    low: 'Low',
  };

  return (
    <span
      className={`px-2 py-1 rounded-full text-xs font-medium ${priorityStyles[priority]} ${className}`}
      aria-label={`Priority: ${priorityLabels[priority]}`}
    >
      {priorityLabels[priority]}
    </span>
  );
};

export default PriorityBadge;
```

### Tag Chips Component

Colored rounded chips for displaying tags:

```tsx
// components/TagChips.tsx
import React from 'react';

interface TagChipsProps {
  tags: string[];
  className?: string;
  onRemove?: (tag: string) => void;
}

const TagChips: React.FC<TagChipsProps> = ({ tags, className = '', onRemove }) => {
  if (!tags || tags.length === 0) return null;

  return (
    <div className={`flex flex-wrap gap-1 ${className}`}>
      {tags.map((tag, index) => (
        <span
          key={index}
          className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200"
          aria-label={`Tag: ${tag}`}
        >
          {tag}
          {onRemove && (
            <button
              type="button"
              className="ml-1 text-blue-600 hover:text-blue-800 focus:outline-none"
              onClick={() => onRemove(tag)}
              aria-label={`Remove tag ${tag}`}
            >
              ×
            </button>
          )}
        </span>
      ))}
    </div>
  );
};

export default TagChips;
```

### Due Date Picker Component

Date picker with calendar interface:

```tsx
// components/DatePicker.tsx
'use client';

import React from 'react';
import { format } from 'date-fns';
import { Calendar as CalendarIcon } from 'lucide-react';

import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';

interface DatePickerProps {
  date: Date | undefined;
  setDate: (date: Date | undefined) => void;
  className?: string;
}

const DatePicker: React.FC<DatePickerProps> = ({ date, setDate, className = '' }) => {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          variant={'outline'}
          className={cn(
            'w-[280px] justify-start text-left font-normal',
            !date && 'text-muted-foreground',
            className
          )}
        >
          <CalendarIcon className="mr-2 h-4 w-4" />
          {date ? format(date, 'PPP') : <span>Pick a date</span>}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0">
        <Calendar
          mode="single"
          selected={date}
          onSelect={setDate}
          initialFocus
        />
      </PopoverContent>
    </Popover>
  );
};

export default DatePicker;
```

### Recurring Toggle Component

Toggle switch for enabling recurring tasks with optional interval selector:

```tsx
// components/RecurringToggle.tsx
import React from 'react';
import { Switch } from '@/components/ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface RecurringToggleProps {
  enabled: boolean;
  interval: string;
  onEnabledChange: (enabled: boolean) => void;
  onIntervalChange: (interval: string) => void;
  className?: string;
}

const RecurringToggle: React.FC<RecurringToggleProps> = ({
  enabled,
  interval,
  onEnabledChange,
  onIntervalChange,
  className = ''
}) => {
  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <Switch
        id="recurring-toggle"
        checked={enabled}
        onCheckedChange={onEnabledChange}
        aria-label="Toggle recurring task"
      />
      <label htmlFor="recurring-toggle" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
        Recurring
      </label>

      {enabled && (
        <Select value={interval} onValueChange={onIntervalChange}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Select interval" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="daily">Daily</SelectItem>
            <SelectItem value="weekly">Weekly</SelectItem>
            <SelectItem value="monthly">Monthly</SelectItem>
            <SelectItem value="yearly">Yearly</SelectItem>
          </SelectContent>
        </Select>
      )}
    </div>
  );
};

export default RecurringToggle;
```

### Sort Dropdown Component

Dropdown for selecting sort options:

```tsx
// components/SortDropdown.tsx
import React from 'react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

type SortOption = 'priority' | 'due_date' | 'title' | 'created_at';

interface SortDropdownProps {
  sortOption: SortOption;
  onSortChange: (option: SortOption) => void;
  className?: string;
}

const SortDropdown: React.FC<SortDropdownProps> = ({ sortOption, onSortChange, className = '' }) => {
  return (
    <Select value={sortOption} onValueChange={(value: SortOption) => onSortChange(value)}>
      <SelectTrigger className={`w-[180px] ${className}`}>
        <SelectValue placeholder="Sort by" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="priority">Priority</SelectItem>
        <SelectItem value="due_date">Due Date</SelectItem>
        <SelectItem value="title">Title</SelectItem>
        <SelectItem value="created_at">Created At</SelectItem>
      </SelectContent>
    </Select>
  );
};

export default SortDropdown;
```

## Task Form Integration

Example of integrating all components into a task form:

```tsx
// components/AdvancedTaskForm.tsx
'use client';

import React, { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import PriorityBadge from '@/components/PriorityBadge';
import TagChips from '@/components/TagChips';
import DatePicker from '@/components/DatePicker';
import RecurringToggle from '@/components/RecurringToggle';
import SortDropdown from '@/components/SortDropdown';

interface TaskFormData {
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low' | null;
  tags: string[];
  dueDate: Date | undefined;
  recurring: boolean;
  recurrenceInterval: string;
}

const AdvancedTaskForm: React.FC = () => {
  const [formData, setFormData] = useState<TaskFormData>({
    title: '',
    description: '',
    priority: null,
    tags: [],
    dueDate: undefined,
    recurring: false,
    recurrenceInterval: 'weekly',
  });

  const [newTag, setNewTag] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
    setFormData({
      ...formData,
      tags: formData.tags.filter(tag => tag !== tagToRemove),
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Submit form data to API
      console.log('Submitting form data:', formData);
      // Add your API submission logic here
    } catch (err) {
      setError('Failed to save task. Please try again.');
      console.error('Error submitting form:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Loading/Error States */}
      {loading && <div className="text-blue-500">Saving...</div>}
      {error && <div className="text-red-500">{error}</div>}

      {/* Title */}
      <div className="space-y-2">
        <Label htmlFor="title">Title</Label>
        <Input
          id="title"
          value={formData.title}
          onChange={(e) => setFormData({...formData, title: e.target.value})}
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
          onChange={(e) => setFormData({...formData, description: e.target.value})}
          placeholder="Task description"
        />
      </div>

      {/* Priority Selector */}
      <div className="space-y-2">
        <Label>Priority</Label>
        <div className="flex space-x-2">
          {(['high', 'medium', 'low'] as const).map(priority => (
            <button
              key={priority}
              type="button"
              className={`px-3 py-1 rounded-md text-sm ${
                formData.priority === priority
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
              onClick={() => setFormData({
                ...formData,
                priority: formData.priority === priority ? null : priority
              })}
            >
              {priority.charAt(0).toUpperCase() + priority.slice(1)}
            </button>
          ))}
        </div>
        {formData.priority && <PriorityBadge priority={formData.priority} />}
      </div>

      {/* Tags */}
      <div className="space-y-2">
        <Label>Tags</Label>
        <div className="flex space-x-2">
          <Input
            value={newTag}
            onChange={(e) => setNewTag(e.target.value)}
            placeholder="Add a tag"
            onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
          />
          <Button type="button" onClick={handleAddTag}>Add</Button>
        </div>
        <TagChips tags={formData.tags} onRemove={handleRemoveTag} />
      </div>

      {/* Due Date */}
      <div className="space-y-2">
        <Label>Due Date</Label>
        <DatePicker
          date={formData.dueDate}
          setDate={(date) => setFormData({...formData, dueDate: date})}
        />
      </div>

      {/* Recurring */}
      <div className="space-y-2">
        <Label>Recurring</Label>
        <RecurringToggle
          enabled={formData.recurring}
          interval={formData.recurrenceInterval}
          onEnabledChange={(enabled) => setFormData({...formData, recurring: enabled})}
          onIntervalChange={(interval) => setFormData({...formData, recurrenceInterval: interval})}
        />
      </div>

      {/* Submit Button */}
      <Button type="submit" disabled={loading}>
        {loading ? 'Saving...' : 'Save Task'}
      </Button>
    </form>
  );
};

export default AdvancedTaskForm;
```

## Responsive Design Guidelines

### Mobile Considerations

- Stack form elements vertically on smaller screens
- Use appropriate spacing that works on touch devices
- Ensure tap targets are at least 44px for accessibility
- Consider using bottom sheets for complex components like date pickers

### Accessibility Features

- Use proper ARIA attributes for all interactive elements
- Ensure sufficient color contrast ratios (4.5:1 for normal text)
- Provide keyboard navigation support
- Include focus indicators for interactive elements
- Use semantic HTML elements where appropriate

## Consistency with Existing UI

When implementing these advanced UI components, maintain consistency with the nextjs-todo-task-ui skill by:

- Following the same color palette and design system
- Using similar component patterns and interactions
- Maintaining the same typography scale
- Keeping consistent spacing and layout patterns
- Following the same loading and error state patterns
