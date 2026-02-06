'use client';

import React, { useEffect, useState } from 'react';

const APP_NOTIFICATIONS_KEY = 'app_notifications_enabled';

interface NotificationPermissionHandlerProps {
  onPermissionChange?: (permission: NotificationPermission) => void;
  onAppToggleChange?: (enabled: boolean) => void;
  className?: string;
}

const NotificationPermissionHandler: React.FC<NotificationPermissionHandlerProps> = ({
  onPermissionChange,
  onAppToggleChange,
  className = ''
}) => {
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const [isSupported, setIsSupported] = useState<boolean>(false);
  const [appNotificationsEnabled, setAppNotificationsEnabled] = useState<boolean>(true);

  useEffect(() => {
    if ('Notification' in window) {
      setIsSupported(true);
      setPermission(Notification.permission);
    } else {
      setIsSupported(false);
    }
    // Load app-level notification preference
    const stored = localStorage.getItem(APP_NOTIFICATIONS_KEY);
    if (stored !== null) {
      setAppNotificationsEnabled(stored === 'true');
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

  const toggleAppNotifications = () => {
    const newValue = !appNotificationsEnabled;
    setAppNotificationsEnabled(newValue);
    localStorage.setItem(APP_NOTIFICATIONS_KEY, String(newValue));
    if (onAppToggleChange) {
      onAppToggleChange(newValue);
    }
    // Dispatch event so useReminderPoller can react
    window.dispatchEvent(new CustomEvent('app-notifications-changed', { detail: newValue }));
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
      <div className={`rounded-lg border ${appNotificationsEnabled ? 'border-green-200 bg-green-50' : 'border-gray-200 bg-gray-50'} p-4 ${className}`}>
        <div className="flex items-center justify-between">
          <div>
            <p className={`text-sm font-medium ${appNotificationsEnabled ? 'text-green-700' : 'text-gray-700'}`}>
              {appNotificationsEnabled ? 'Notifications Enabled' : 'Notifications Paused'}
            </p>
            <p className={`text-sm mt-1 ${appNotificationsEnabled ? 'text-green-600' : 'text-gray-500'}`}>
              {appNotificationsEnabled
                ? 'You will receive reminders for your tasks.'
                : 'Task reminders are currently paused.'}
            </p>
          </div>
          <button
            type="button"
            onClick={toggleAppNotifications}
            className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${
              appNotificationsEnabled ? 'bg-green-500' : 'bg-gray-300'
            }`}
            role="switch"
            aria-checked={appNotificationsEnabled}
          >
            <span
              className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                appNotificationsEnabled ? 'translate-x-5' : 'translate-x-0'
              }`}
            />
          </button>
        </div>
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
