/**
 * API utilities for handling task operations with authentication.
 * This follows the API contract specified in the requirements.
 */

import { getAccessToken, apiCall as baseApiCall } from './auth';

// Define the Task type
export type Task = {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
  user_id: string;
};

// Function to get all tasks for the current user
export const getTasks = async (): Promise<Task[]> => {
  try {
    const response = await baseApiCall('/api/v1/tasks/', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch tasks: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching tasks:', error);
    throw error;
  }
};

// Function to create a new task
export const createTask = async (taskData: { title: string; description?: string }): Promise<Task> => {
  try {
    const response = await baseApiCall('/api/v1/tasks/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(taskData),
    });

    if (!response.ok) {
      throw new Error(`Failed to create task: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error creating task:', error);
    throw error;
  }
};

// Function to update an existing task
export const updateTask = async (id: number, taskData: { title?: string; description?: string; completed?: boolean }): Promise<Task> => {
  try {
    const response = await baseApiCall(`/api/v1/tasks/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(taskData),
    });

    if (!response.ok) {
      throw new Error(`Failed to update task: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error updating task:', error);
    throw error;
  }
};

// Function to delete a task
export const deleteTask = async (id: number): Promise<boolean> => {
  try {
    const response = await baseApiCall(`/api/v1/tasks/${id}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`Failed to delete task: ${response.status} ${response.statusText}`);
    }

    // For DELETE requests, the API returns 204 No Content
    return response.status === 204;
  } catch (error) {
    console.error('Error deleting task:', error);
    throw error;
  }
};

// Function to toggle task completion status
export const toggleTaskCompletion = async (id: number): Promise<Task> => {
  try {
    const response = await baseApiCall(`/api/v1/tasks/${id}/complete`, {
      method: 'PATCH',
    });

    if (!response.ok) {
      throw new Error(`Failed to toggle task completion: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error toggling task completion:', error);
    throw error;
  }
};

// Export the base apiCall function for other uses
export { apiCall } from './auth';