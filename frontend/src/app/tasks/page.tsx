'use client';

import React from 'react';
import TaskList from '@/components/TaskList';
import { useAuth } from '@/hooks/useAuth';

export default function TasksPage() {
  const { state } = useAuth();

  // If user is not authenticated, redirect to login (this would be handled by a wrapper in a real app)
  if (!state.isAuthenticated && !state.isLoading) {
    // In a real app, we would redirect to login page
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
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">Todo Tasks</h1>
        </div>
      </header>
      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
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
    </div>
  );
}