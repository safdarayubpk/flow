'use client';

import React, { useState } from 'react';
import RecurrenceEditor from './RecurrenceEditor';

interface RecurringToggleProps {
  enabled: boolean;
  onToggle: (enabled: boolean, rule?: string) => void;
  initialRule?: string;
  className?: string;
}

const RecurringToggle: React.FC<RecurringToggleProps> = ({
  enabled,
  onToggle,
  initialRule = 'FREQ=DAILY',
  className = ''
}) => {
  const [showEditor, setShowEditor] = useState(false);
  const [tempRule, setTempRule] = useState(initialRule);

  const handleToggle = () => {
    if (!enabled) {
      onToggle(true, tempRule);
    } else {
      onToggle(false);
      setShowEditor(false);
    }
  };

  const handleRuleChange = (rule: string) => {
    setTempRule(rule);
    if (enabled) {
      onToggle(true, rule);
    }
  };

  return (
    <div className={`space-y-3 ${className}`}>
      <div className="flex items-center space-x-3">
        <button
          type="button"
          role="switch"
          aria-checked={enabled}
          onClick={handleToggle}
          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
            enabled ? 'bg-indigo-600' : 'bg-gray-200'
          }`}
        >
          <span
            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
              enabled ? 'translate-x-6' : 'translate-x-1'
            }`}
          />
        </button>
        <span className="text-sm font-medium text-gray-700">Recurring</span>

        {enabled && (
          <button
            type="button"
            onClick={() => setShowEditor(!showEditor)}
            className="px-3 py-1 text-sm rounded-md border border-gray-300 text-gray-600 hover:bg-gray-50"
          >
            {showEditor ? 'Hide' : 'Configure'}
          </button>
        )}
      </div>

      {enabled && showEditor && (
        <div className="border rounded-lg p-4 bg-gray-50">
          <RecurrenceEditor
            rule={tempRule}
            onRuleChange={handleRuleChange}
          />
        </div>
      )}
    </div>
  );
};

export default RecurringToggle;
