'use client';

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