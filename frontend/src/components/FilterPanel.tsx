'use client';

import React, { useState } from 'react';

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

  const handlePriorityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    onFilterChange({ ...filters, priority: value === 'all' ? null : value });
  };

  const handleTagToggle = (tag: string) => {
    const newTags = selectedTags.includes(tag)
      ? selectedTags.filter(t => t !== tag)
      : [...selectedTags, tag];

    setSelectedTags(newTags);
    onFilterChange({ ...filters, tags: newTags });
  };

  const handleDueDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    onFilterChange({ ...filters, dueDateBefore: value ? new Date(value) : null });
  };

  const handleRecurringChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFilterChange({ ...filters, recurring: e.target.checked ? true : null });
  };

  const clearFilters = () => {
    setSelectedTags([]);
    onFilterChange({ priority: null, tags: [], dueDateBefore: null, recurring: null });
  };

  const formatDateForInput = (d: Date | null | undefined): string => {
    if (!d) return '';
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  return (
    <div className={`border rounded-lg p-4 space-y-4 ${className}`}>
      <div className="flex justify-between items-center">
        <h3 className="font-medium text-gray-800">Filters</h3>
        <button
          type="button"
          onClick={clearFilters}
          className="px-3 py-1 text-sm rounded-md border border-gray-300 text-gray-600 hover:bg-gray-50"
        >
          Clear All
        </button>
      </div>

      {/* Priority Filter */}
      <div className="space-y-1">
        <label htmlFor="priority-filter" className="block text-sm font-medium text-gray-700">Priority</label>
        <select
          id="priority-filter"
          value={filters.priority || 'all'}
          onChange={handlePriorityChange}
          className="w-full rounded-md border border-gray-300 py-2 px-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none bg-white"
        >
          <option value="all">All Priorities</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      {/* Tags Filter */}
      {availableTags.length > 0 && (
        <div className="space-y-1">
          <span className="block text-sm font-medium text-gray-700">Tags</span>
          <div className="flex flex-wrap gap-2">
            {availableTags.map((tag) => (
              <label key={tag} className="flex items-center space-x-1.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedTags.includes(tag)}
                  onChange={() => handleTagToggle(tag)}
                  className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                <span className="text-sm text-gray-600">{tag}</span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Due Date Filter */}
      <div className="space-y-1">
        <label htmlFor="due-before" className="block text-sm font-medium text-gray-700">Due Before</label>
        <input
          id="due-before"
          type="date"
          value={formatDateForInput(filters.dueDateBefore)}
          onChange={handleDueDateChange}
          className="w-full rounded-md border border-gray-300 py-2 px-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none"
        />
      </div>

      {/* Recurring Filter */}
      <label className="flex items-center space-x-2 pt-2 cursor-pointer">
        <input
          type="checkbox"
          checked={filters.recurring === true}
          onChange={handleRecurringChange}
          className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
        />
        <span className="text-sm text-gray-600">Recurring Tasks Only</span>
      </label>
    </div>
  );
};

export default FilterPanel;
