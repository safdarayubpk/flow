'use client';

'use client';

import React, { useState } from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Calendar } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { CalendarIcon } from 'lucide-react';
import { format } from 'date-fns';

interface FilterOptions {
  priority?: string | null;
  tags?: string[];
  dueDateBefore?: Date | null;
  recurring?: boolean | null;
}

interface FilterPanelProps {
  filters: FilterOptions;
  onFilterChange: (filters: FilterOptions) => void;
  availableTags?: string[];
  className?: string;
}

const FilterPanel: React.FC<FilterPanelProps> = ({
  filters,
  onFilterChange,
  availableTags = [],
  className = ''
}) => {
  const [selectedTags, setSelectedTags] = useState<string[]>(filters.tags || []);
  const [datePickerOpen, setDatePickerOpen] = useState(false);

  const handlePriorityChange = (value: string) => {
    onFilterChange({ ...filters, priority: value === 'all' ? null : value });
  };

  const handleTagToggle = (tag: string) => {
    const newTags = selectedTags.includes(tag)
      ? selectedTags.filter(t => t !== tag)
      : [...selectedTags, tag];

    setSelectedTags(newTags);
    onFilterChange({ ...filters, tags: newTags });
  };

  const handleDueDateChange = (date: Date | undefined) => {
    onFilterChange({ ...filters, dueDateBefore: date || null });
    setDatePickerOpen(false);
  };

  const handleRecurringChange = (checked: boolean) => {
    onFilterChange({ ...filters, recurring: checked ? true : null });
  };

  const clearFilters = () => {
    const clearedFilters: FilterOptions = {
      priority: null,
      tags: [],
      dueDateBefore: null,
      recurring: null
    };
    setSelectedTags([]);
    onFilterChange(clearedFilters);
  };

  return (
    <div className={`border rounded-lg p-4 space-y-4 ${className}`}>
      <div className="flex justify-between items-center">
        <h3 className="font-medium">Filters</h3>
        <Button type="button" variant="outline" size="sm" onClick={clearFilters}>
          Clear All
        </Button>
      </div>

      {/* Priority Filter */}
      <div className="space-y-2">
        <Label htmlFor="priority-filter">Priority</Label>
        <Select value={filters.priority || 'all'} onValueChange={handlePriorityChange}>
          <SelectTrigger id="priority-filter" className="w-full">
            <SelectValue placeholder="Select priority" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Priorities</SelectItem>
            <SelectItem value="high">High</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="low">Low</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Tags Filter */}
      <div className="space-y-2">
        <Label>Tags</Label>
        <div className="flex flex-wrap gap-2">
          {availableTags.map((tag) => (
            <div key={tag} className="flex items-center space-x-2">
              <Checkbox
                id={`tag-${tag}`}
                checked={selectedTags.includes(tag)}
                onCheckedChange={() => handleTagToggle(tag)}
              />
              <Label htmlFor={`tag-${tag}`} className="text-sm font-normal">
                {tag}
              </Label>
            </div>
          ))}
        </div>
      </div>

      {/* Due Date Filter */}
      <div className="space-y-2">
        <Label>Due Before</Label>
        <Popover open={datePickerOpen} onOpenChange={setDatePickerOpen}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              className={`w-full justify-start text-left font-normal ${
                !filters.dueDateBefore && 'text-muted-foreground'
              }`}
            >
              <CalendarIcon className="mr-2 h-4 w-4" />
              {filters.dueDateBefore ? format(filters.dueDateBefore, 'PPP') : <span>Pick a date</span>}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0">
            <Calendar
              mode="single"
              selected={filters.dueDateBefore || undefined}
              onSelect={handleDueDateChange}
              initialFocus
            />
          </PopoverContent>
        </Popover>
      </div>

      {/* Recurring Filter */}
      <div className="flex items-center space-x-2 pt-2">
        <Checkbox
          id="recurring-filter"
          checked={filters.recurring === true}
          onCheckedChange={(checked) => handleRecurringChange(checked as boolean)}
        />
        <Label htmlFor="recurring-filter" className="text-sm font-normal">
          Recurring Tasks Only
        </Label>
      </div>
    </div>
  );
};

export default FilterPanel;