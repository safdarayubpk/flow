'use client';

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