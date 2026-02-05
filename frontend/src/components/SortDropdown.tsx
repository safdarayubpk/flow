'use client';

import React from 'react';

type SortOption = 'priority' | 'due_date' | 'title' | 'created_at';

interface SortDropdownProps {
  sortOption: SortOption;
  sortOrder: 'asc' | 'desc';
  onSortChange: (option: SortOption) => void;
  className?: string;
}

const sortLabels: Record<SortOption, string> = {
  priority: 'Priority',
  due_date: 'Due Date',
  title: 'Title',
  created_at: 'Created At',
};

const SortDropdown: React.FC<SortDropdownProps> = ({ sortOption, sortOrder, onSortChange, className = '' }) => {
  return (
    <select
      value={sortOption}
      onChange={(e) => onSortChange(e.target.value as SortOption)}
      className={`rounded-md border border-gray-300 py-2 px-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none bg-white ${className}`}
    >
      {(Object.keys(sortLabels) as SortOption[]).map((key) => (
        <option key={key} value={key}>
          {sortLabels[key]} {sortOption === key ? (sortOrder === 'asc' ? '\u2191' : '\u2193') : ''}
        </option>
      ))}
    </select>
  );
};

export default SortDropdown;
