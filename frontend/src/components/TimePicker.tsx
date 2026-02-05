'use client';

import React from 'react';

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
  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <span className="text-sm font-medium text-gray-700">Time</span>
      <input
        type="time"
        value={time}
        onChange={(e) => onTimeChange(e.target.value)}
        className="rounded-md border border-gray-300 py-2 px-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none"
      />
    </div>
  );
};

export default TimePicker;
