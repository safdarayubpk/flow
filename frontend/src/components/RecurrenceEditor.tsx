'use client';

import React, { useState } from 'react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

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

  const [interval, setInterval] = useState<string>(() => {
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

  const updateRule = () => {
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
  };

  React.useEffect(() => {
    updateRule();
  }, [frequency, interval, count, until]);

  const handleFrequencyChange = (value: string) => {
    setFrequency(value);
  };

  const handleIntervalChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    if (value === '' || /^[1-9]\d*$/.test(value)) {
      setInterval(value);
    }
  };

  const handleCountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    if (value === '' || /^[1-9]\d*$/.test(value)) {
      setCount(value);
    }
  };

  const handleUntilChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUntil(e.target.value);
  };

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label>Frequency</Label>
          <Select value={frequency} onValueChange={handleFrequencyChange}>
            <SelectTrigger>
              <SelectValue placeholder="Select frequency" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">None</SelectItem>
              <SelectItem value="daily">Daily</SelectItem>
              <SelectItem value="weekly">Weekly</SelectItem>
              <SelectItem value="monthly">Monthly</SelectItem>
              <SelectItem value="yearly">Yearly</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label>Interval</Label>
          <Input
            type="number"
            min="1"
            value={interval}
            onChange={handleIntervalChange}
            placeholder="Every X times"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label>End After (occurrences)</Label>
          <Input
            type="number"
            min="1"
            value={count}
            onChange={handleCountChange}
            placeholder="Leave empty for no end"
          />
        </div>

        <div className="space-y-2">
          <Label>End By Date</Label>
          <Input
            type="date"
            value={until}
            onChange={handleUntilChange}
            placeholder="YYYYMMDDTHHMMSSZ"
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