'use client';

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
  sortOrder: 'asc' | 'desc';
  onSortChange: (option: SortOption) => void;
  className?: string;
}

const SortDropdown: React.FC<SortDropdownProps> = ({ sortOption, sortOrder, onSortChange, className = '' }) => {
  return (
    <Select value={sortOption} onValueChange={(value: SortOption) => onSortChange(value)}>
      <SelectTrigger className={`w-[180px] ${className}`}>
        <SelectValue>
          {sortOption.charAt(0).toUpperCase() + sortOption.slice(1)} {sortOrder === 'asc' ? '↑' : '↓'}
        </SelectValue>
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