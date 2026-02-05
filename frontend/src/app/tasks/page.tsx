'use client';

import React from 'react';
import TaskList from '@/components/TaskList';
import ChatWidget from '@/components/ChatWidget';
import NotificationPermissionHandler from '@/components/NotificationPermissionHandler';
import { useAuth } from '@/hooks/useAuth';

export default function TasksPage() {
  const { state, logout } = useAuth();

  // Show loading spinner while checking auth
  if (state.isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // If user is not authenticated, redirect to login
  if (!state.isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800">Please log in to view tasks</h2>
          <a href="/login" className="mt-4 inline-block px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
            Go to Login
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-4 sm:py-6 px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 sm:gap-0">
          <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-6 w-full sm:w-auto">
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Todo Tasks</h1>
            <nav className="flex gap-4">
              <a
                href="/tasks"
                className="text-indigo-600 font-medium border-b-2 border-indigo-600 pb-1 min-h-[44px] sm:min-h-0 flex items-center"
              >
                Tasks
              </a>
              <a
                href="/chat"
                className="text-gray-500 hover:text-indigo-600 font-medium pb-1 min-h-[44px] sm:min-h-0 flex items-center"
              >
                AI Chat
              </a>
            </nav>
          </div>
          <div className="flex items-center gap-3 sm:gap-4 w-full sm:w-auto justify-between sm:justify-end">
            {state.user && (
              <span className="text-xs sm:text-sm text-gray-600 truncate max-w-[150px] sm:max-w-none">{state.user.email}</span>
            )}
            <button
              onClick={logout}
              className="px-3 sm:px-4 py-2.5 sm:py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 min-h-[44px] sm:min-h-0"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>
      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <NotificationPermissionHandler className="mb-4" />
            <div className="bg-white shadow rounded-lg p-6">
              {state.user ? (
                <TaskList userId={state.user.id} />
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-500">Loading tasks...</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Chat Widget */}
      <ChatWidget />
    </div>
  );
}