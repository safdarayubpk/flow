'use client';

import React, { useState } from 'react';
import { Clock } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface TimePickerProps {
  time: string; // Format: "HH:MM" (24-hour format)
  onTimeChange: (time: string) => void;
  className?: string;
}

const TimePicker: React.FC<TimePickerProps> = ({
  time = '09:00',
  onTimeChange,
  className = ''
}) => {
  const [hours, setHours] = useState<string>(time.split(':')[0]);
  const [minutes, setMinutes] = useState<string>(time.split(':')[1]);

  const handleHoursChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    if (value === '' || (/^\d+$/.test(value) && parseInt(value) >= 0 && parseInt(value) <= 23)) {
      setHours(value);
      onTimeChange(`${value.padStart(2, '0')}:${minutes}`);
    }
  };

  const handleMinutesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    if (value === '' || (/^\d+$/.test(value) && parseInt(value) >= 0 && parseInt(value) <= 59)) {
      setMinutes(value);
      onTimeChange(`${hours}:${value.padStart(2, '0')}`);
    }
  };

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <div className="flex items-center space-x-1">
        <Clock className="h-4 w-4 text-gray-500" />
        <Label className="text-sm font-medium">Time</Label>
      </div>
      <div className="flex space-x-1">
        <Input
          type="number"
          min="0"
          max="23"
          value={hours}
          onChange={handleHoursChange}
          className="w-16 text-center"
          placeholder="HH"
        />
        <span className="self-center">:</span>
        <Input
          type="number"
          min="0"
          max="59"
          value={minutes}
          onChange={handleMinutesChange}
          className="w-16 text-center"
          placeholder="MM"
        />
      </div>
    </div>
  );
};

export default TimePicker;