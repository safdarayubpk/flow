'use client';

import React, { useState, useEffect } from 'react';

interface RecurrenceEditorProps {
  rule: string;
  onRuleChange: (rule: string) => void;
  className?: string;
}

const RecurrenceEditor: React.FC<RecurrenceEditorProps> = ({
  rule,
  onRuleChange,
  className = ''
}) => {
  const [frequency, setFrequency] = useState<string>(() => {
    if (rule.includes('FREQ=DAILY')) return 'daily';
    if (rule.includes('FREQ=WEEKLY')) return 'weekly';
    if (rule.includes('FREQ=MONTHLY')) return 'monthly';
    if (rule.includes('FREQ=YEARLY')) return 'yearly';
    return 'none';
  });

  const [interval, setIntervalVal] = useState<string>(() => {
    const match = rule.match(/INTERVAL=(\d+)/);
    return match ? match[1] : '1';
  });

  const [count, setCount] = useState<string>(() => {
    const match = rule.match(/COUNT=(\d+)/);
    return match ? match[1] : '';
  });

  const [until, setUntil] = useState<string>(() => {
    const match = rule.match(/UNTIL=([^;]+)/);
    return match ? match[1] : '';
  });

  useEffect(() => {
    let newRule = `FREQ=${frequency.toUpperCase()}`;
    if (interval && interval !== '1') {
      newRule += `;INTERVAL=${interval}`;
    }
    if (count) {
      newRule += `;COUNT=${count}`;
    } else if (until) {
      newRule += `;UNTIL=${until}`;
    }
    onRuleChange(newRule);
  }, [frequency, interval, count, until]);

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-700">Frequency</label>
          <select
            value={frequency}
            onChange={(e) => setFrequency(e.target.value)}
            className="w-full rounded-md border border-gray-300 py-2 px-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none bg-white"
          >
            <option value="none">None</option>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="yearly">Yearly</option>
          </select>
        </div>

        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-700">Interval</label>
          <input
            type="number"
            min="1"
            value={interval}
            onChange={(e) => {
              const v = e.target.value;
              if (v === '' || /^[1-9]\d*$/.test(v)) setIntervalVal(v);
            }}
            placeholder="Every X times"
            className="w-full rounded-md border border-gray-300 py-2 px-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-700">End After (occurrences)</label>
          <input
            type="number"
            min="1"
            value={count}
            onChange={(e) => {
              const v = e.target.value;
              if (v === '' || /^[1-9]\d*$/.test(v)) setCount(v);
            }}
            placeholder="Leave empty for no end"
            className="w-full rounded-md border border-gray-300 py-2 px-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none"
          />
        </div>

        <div className="space-y-1">
          <label className="block text-sm font-medium text-gray-700">End By Date</label>
          <input
            type="date"
            value={until}
            onChange={(e) => setUntil(e.target.value)}
            className="w-full rounded-md border border-gray-300 py-2 px-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none"
          />
        </div>
      </div>

      <div className="text-sm text-gray-500 p-3 bg-gray-50 rounded-md">
        <strong>Generated Rule:</strong> {rule}
      </div>
    </div>
  );
};

export default RecurrenceEditor;
