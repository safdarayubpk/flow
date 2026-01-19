import React, { useState, useEffect } from 'react';
import TaskCard from './TaskCard';
import TaskForm from './TaskForm';
import { apiCall } from '@/lib/api';

// Define the Task type
type Task = {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
  user_id: string;
};

interface TaskListProps {
  userId: string;
}

export default function TaskList({ userId }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  // Fetch tasks when component mounts or when tasks change
  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await apiCall('/api/v1/tasks/', {
        method: 'GET',
      });

      if (response.ok) {
        const tasksData = await response.json();
        setTasks(tasksData);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to fetch tasks');
      }
    } catch (err) {
      setError('An error occurred while fetching tasks');
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleTask = async (id: number) => {
    try {
      const response = await apiCall(`/api/v1/tasks/${id}/complete`, {
        method: 'PATCH',
      });

      if (response.ok) {
        const updatedTask = await response.json();
        setTasks(tasks.map(task =>
          task.id === id ? { ...task, completed: updatedTask.completed } : task
        ));
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to update task');
      }
    } catch (err) {
      setError('An error occurred while updating the task');
      console.error('Error updating task:', err);
    }
  };

  const handleDeleteTask = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      const response = await apiCall(`/api/v1/tasks/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setTasks(tasks.filter(task => task.id !== id));
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to delete task');
      }
    } catch (err) {
      setError('An error occurred while deleting the task');
      console.error('Error deleting task:', err);
    }
  };

  const handleEditTask = (task: Task) => {
    setEditingTask(task);
    setShowForm(true);
  };

  const handleCreateTask = () => {
    setEditingTask(null);
    setShowForm(true);
  };

  const handleSubmitTask = async (taskData: { id?: number; title: string; description?: string }) => {
    try {
      let response;

      if (taskData.id) {
        // Update existing task
        response = await apiCall(`/api/v1/tasks/${taskData.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            title: taskData.title,
            description: taskData.description,
          }),
        });
      } else {
        // Create new task
        response = await apiCall('/api/v1/tasks/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            title: taskData.title,
            description: taskData.description,
          }),
        });
      }

      if (response.ok) {
        const newTask = await response.json();

        if (taskData.id) {
          // Update existing task in the list
          setTasks(tasks.map(task =>
            task.id === taskData.id ? newTask : task
          ));
        } else {
          // Add new task to the list
          setTasks([newTask, ...tasks]);
        }

        // Close the form
        setShowForm(false);
        setEditingTask(null);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to save task');
      }
    } catch (err) {
      setError('An error occurred while saving the task');
      console.error('Error saving task:', err);
    }
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setEditingTask(null);
  };

  if (loading) {
    return <div className="text-center py-8">Loading tasks...</div>;
  }

  if (error) {
    return <div className="text-center py-8 text-red-500">{error}</div>;
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-gray-800">Your Tasks</h2>
        <button
          onClick={handleCreateTask}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Add Task
        </button>
      </div>

      {showForm && (
        <TaskForm
          onSubmit={handleSubmitTask}
          onCancel={handleCancelForm}
          initialData={editingTask || undefined}
        />
      )}

      {tasks.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          No tasks found. Create your first task!
        </div>
      ) : (
        <div>
          {tasks.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onToggle={handleToggleTask}
              onDelete={handleDeleteTask}
              onEdit={handleEditTask}
            />
          ))}
        </div>
      )}
    </div>
  );
}