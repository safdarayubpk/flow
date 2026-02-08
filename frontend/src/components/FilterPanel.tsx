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
  const [isExpanded, setIsExpanded] = useState<boolean>(false);

  // Count active filters for badge
  const activeFilterCount = [
    filters.priority,
    filters.tags && filters.tags.length > 0,
    filters.dueDateBefore,
    filters.recurring
  ].filter(Boolean).length;

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
    <div className={`border rounded-lg ${className}`}>
      {/* Collapsible Header */}
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors rounded-lg"
      >
        <div className="flex items-center gap-2">
          <span className="font-medium text-gray-800">Filters</span>
          {activeFilterCount > 0 && (
            <span className="inline-flex items-center justify-center px-2 py-0.5 text-xs font-medium bg-indigo-100 text-indigo-700 rounded-full">
              {activeFilterCount}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          {activeFilterCount > 0 && (
            <span
              onClick={(e) => { e.stopPropagation(); clearFilters(); }}
              className="text-sm text-gray-500 hover:text-gray-700 cursor-pointer hover:underline"
            >
              Clear All
            </span>
          )}
          <svg
            className={`h-4 w-4 text-gray-500 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Collapsible Content */}
      {isExpanded && (
        <div className="px-4 pb-4 space-y-4 border-t">
          {/* Priority Filter */}
          <div className="space-y-1 pt-4">
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
      )}
    </div>
  );
};

export default FilterPanel;
