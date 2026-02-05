'use client';

import React, { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Bell, BellOff, Settings } from 'lucide-react';

interface NotificationPermissionHandlerProps {
  onPermissionChange?: (permission: NotificationPermission) => void;
  className?: string;
}

const NotificationPermissionHandler: React.FC<NotificationPermissionHandlerProps> = ({
  onPermissionChange,
  className = ''
}) => {
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const [isSupported, setIsSupported] = useState<boolean>(false);

  useEffect(() => {
    // Check if browser supports notifications
    if ('Notification' in window) {
      setIsSupported(true);
      setPermission(Notification.permission);
    } else {
      setIsSupported(false);
    }
  }, []);

  const requestPermission = async () => {
    if (!isSupported) return;

    try {
      const result = await Notification.requestPermission();
      setPermission(result);
      if (onPermissionChange) {
        onPermissionChange(result);
      }
    } catch (error) {
      console.error('Error requesting notification permission:', error);
    }
  };

  if (!isSupported) {
    return (
      <Alert className={className}>
        <BellOff className="h-4 w-4" />
        <AlertTitle>Notifications not supported</AlertTitle>
        <AlertDescription>
          Your browser does not support desktop notifications. You may still receive in-app notifications.
        </AlertDescription>
      </Alert>
    );
  }

  if (permission === 'granted') {
    return (
      <Alert className={`${className} border-green-200 bg-green-50`}>
        <Bell className="h-4 w-4 text-green-600" />
        <AlertTitle>Notifications Enabled</AlertTitle>
        <AlertDescription>
          You have granted permission to receive browser notifications.
        </AlertDescription>
      </Alert>
    );
  }

  if (permission === 'denied') {
    return (
      <Alert className={`${className} border-red-200 bg-red-50`}>
        <BellOff className="h-4 w-4 text-red-600" />
        <AlertTitle>Notifications Blocked</AlertTitle>
        <AlertDescription>
          You have blocked browser notifications. Please enable them in your browser settings.
        </AlertDescription>
        <div className="mt-2">
          <Button variant="outline" size="sm" onClick={() => window.open('about:blank', '_blank')}>
            <Settings className="h-4 w-4 mr-2" />
            Open Settings
          </Button>
        </div>
      </Alert>
    );
  }

  // Default state - permission not yet requested
  return (
    <Alert className={className}>
      <Bell className="h-4 w-4" />
      <AlertTitle>Enable Notifications</AlertTitle>
      <AlertDescription>
        Enable browser notifications to receive reminders for your tasks.
      </AlertDescription>
      <div className="mt-2">
        <Button variant="default" size="sm" onClick={requestPermission}>
          Enable Notifications
        </Button>
      </div>
    </Alert>
  );
};

export default NotificationPermissionHandler;