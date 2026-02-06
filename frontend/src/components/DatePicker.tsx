'use client';

import React from 'react';

interface DatePickerProps {
  date: Date | undefined;
  onDateChange: (date: Date | undefined) => void;
  placeholder?: string;
  className?: string;
}

const DatePicker: React.FC<DatePickerProps> = ({ date, onDateChange, placeholder = 'Select date', className = '' }) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    if (value) {
      // Parse as local date, not UTC
      // new Date("2026-02-06") parses as UTC midnight, which causes timezone issues
      const [year, month, day] = value.split('-').map(Number);
      onDateChange(new Date(year, month - 1, day));
    } else {
      onDateChange(undefined);
    }
  };

  const formatForInput = (d: Date | undefined): string => {
    if (!d) return '';
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  return (
    <input
      type="date"
      value={formatForInput(date)}
      onChange={handleChange}
      placeholder={placeholder}
      className={`rounded-md border border-gray-300 py-2 px-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none ${className}`}
    />
  );
};

export default DatePicker;
