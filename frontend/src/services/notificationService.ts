/**
 * Service for handling both browser notifications and in-app toasts
 */
import { toast } from 'sonner'; // Assuming we're using sonner for toasts

export interface NotificationOptions {
  title: string;
  body?: string;
  icon?: string;
  tag?: string;
  silent?: boolean;
  requireInteraction?: boolean;
}

class NotificationService {
  /**
   * Show a notification using browser's Notification API or fallback to in-app toast
   */
  static showNotification(options: NotificationOptions): void {
    // Check if browser notifications are supported and enabled
    if ('Notification' in window) {
      // Check permission
      if (Notification.permission === 'granted') {
        // Browser notification
        new Notification(options.title, {
          body: options.body,
          icon: options.icon,
          tag: options.tag,
          silent: options.silent,
          requireInteraction: options.requireInteraction
        });
      } else if (Notification.permission === 'default') {
        // Request permission and then show notification
        Notification.requestPermission().then(permission => {
          if (permission === 'granted') {
            new Notification(options.title, {
              body: options.body,
              icon: options.icon,
              tag: options.tag,
              silent: options.silent,
              requireInteraction: options.requireInteraction
            });
          } else {
            // Fallback to in-app notification
            this.showInAppNotification(options);
          }
        });
      } else {
        // Permission denied, use in-app notification
        this.showInAppNotification(options);
      }
    } else {
      // Browser doesn't support notifications, use in-app
      this.showInAppNotification(options);
    }
  }

  /**
   * Show an in-app notification using toast
   */
  static showInAppNotification(options: NotificationOptions): void {
    toast(options.title, {
      description: options.body,
      duration: 5000, // Show for 5 seconds
    });
  }

  /**
   * Schedule a notification for a specific time
   */
  static scheduleNotification(options: NotificationOptions, delayMs: number): number {
    return setTimeout(() => {
      this.showNotification(options);
    }, delayMs) as unknown as number;
  }

  /**
   * Cancel a scheduled notification
   */
  static cancelScheduledNotification(timeoutId: number): void {
    clearTimeout(timeoutId);
  }

  /**
   * Check if notifications are supported
   */
  static isSupported(): boolean {
    return 'Notification' in window;
  }

  /**
   * Get current notification permission status
   */
  static getPermission(): NotificationPermission {
    if ('Notification' in window) {
      return Notification.permission;
    }
    return 'denied'; // Not supported
  }

  /**
   * Request notification permission
   */
  static async requestPermission(): Promise<NotificationPermission> {
    if ('Notification' in window) {
      return await Notification.requestPermission();
    }
    return 'denied';
  }
}

export default NotificationService;