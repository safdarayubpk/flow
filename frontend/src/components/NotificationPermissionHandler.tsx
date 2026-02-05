'use client';

import React, { useEffect, useState } from 'react';

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
      <div className={`rounded-lg border border-gray-200 p-4 ${className}`}>
        <p className="text-sm font-medium text-gray-700">Notifications not supported</p>
        <p className="text-sm text-gray-500 mt-1">
          Your browser does not support desktop notifications. You may still receive in-app notifications.
        </p>
      </div>
    );
  }

  if (permission === 'granted') {
    return (
      <div className={`rounded-lg border border-green-200 bg-green-50 p-4 ${className}`}>
        <p className="text-sm font-medium text-green-700">Notifications Enabled</p>
        <p className="text-sm text-green-600 mt-1">
          You have granted permission to receive browser notifications.
        </p>
      </div>
    );
  }

  if (permission === 'denied') {
    return (
      <div className={`rounded-lg border border-red-200 bg-red-50 p-4 ${className}`}>
        <p className="text-sm font-medium text-red-700">Notifications Blocked</p>
        <p className="text-sm text-red-600 mt-1">
          You have blocked browser notifications. Please enable them in your browser settings.
        </p>
      </div>
    );
  }

  return (
    <div className={`rounded-lg border border-gray-200 p-4 ${className}`}>
      <p className="text-sm font-medium text-gray-700">Enable Notifications</p>
      <p className="text-sm text-gray-500 mt-1">
        Enable browser notifications to receive reminders for your tasks.
      </p>
      <button
        type="button"
        onClick={requestPermission}
        className="mt-2 px-3 py-1.5 text-sm font-medium rounded-md bg-indigo-600 text-white hover:bg-indigo-700"
      >
        Enable Notifications
      </button>
    </div>
  );
};

export default NotificationPermissionHandler;
