'use client';

import React, { useState } from 'react';
import { Switch } from '@/components/ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
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
  const [dialogOpen, setDialogOpen] = useState(false);
  const [tempRule, setTempRule] = useState(initialRule);

  const handleSwitchChange = (checked: boolean) => {
    if (checked) {
      // Enable recurring with the current rule
      onToggle(true, tempRule);
    } else {
      // Disable recurring
      onToggle(false);
    }
  };

  const handleRuleChange = (rule: string) => {
    setTempRule(rule);
    if (enabled) {
      // If already enabled, update the rule immediately
      onToggle(true, rule);
    } else {
      // Otherwise, just update the temp rule for when it gets enabled
      setTempRule(rule);
    }
  };

  const handleDialogClose = () => {
    setDialogOpen(false);
  };

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <Switch
        id="recurring-toggle"
        checked={enabled}
        onCheckedChange={handleSwitchChange}
        aria-label="Toggle recurring task"
      />
      <label htmlFor="recurring-toggle" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
        Recurring
      </label>

      {enabled && (
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm">
              Configure
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Configure Recurring Task</DialogTitle>
            </DialogHeader>
            <RecurrenceEditor
              rule={initialRule}
              onRuleChange={handleRuleChange}
            />
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
};

export default RecurringToggle;