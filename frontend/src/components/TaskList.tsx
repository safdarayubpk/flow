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

  // Fetch tasks when component mounts
  useEffect(() => {
    fetchTasks();
  }, []);

  // Listen for task updates from chat widget
  useEffect(() => {
    const handleTaskUpdate = () => {
      fetchTasks();
    };

    window.addEventListener('tasks-updated', handleTaskUpdate);
    return () => {
      window.removeEventListener('tasks-updated', handleTaskUpdate);
    };
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

  const handleEditTask = (id: number) => {
    const taskToEdit = tasks.find(task => task.id === id);
    if (taskToEdit) {
      setEditingTask(taskToEdit);
      setShowForm(true);
    }
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

  const [showCompleted, setShowCompleted] = useState(true);

  // Separate active and completed tasks
  const activeTasks = tasks.filter(task => !task.completed);
  const completedTasks = tasks.filter(task => task.completed);

  if (loading) {
    return <div className="text-center py-8">Loading tasks...</div>;
  }

  if (error) {
    return <div className="text-center py-8 text-red-500">{error}</div>;
  }

  return (
    <div>
      {/* Header with Add Task button */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-6">
        <h2 className="text-lg sm:text-xl font-bold text-gray-800">
          Your Tasks
          <span className="block sm:inline sm:ml-2 text-sm font-normal text-gray-500">
            ({activeTasks.length} active, {completedTasks.length} completed)
          </span>
        </h2>
        <button
          onClick={handleCreateTask}
          className="inline-flex items-center px-4 py-2.5 sm:py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 min-h-[44px] sm:min-h-0 w-full sm:w-auto justify-center"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Add Task
        </button>
      </div>

      {showForm && (
        <TaskForm
          key={editingTask?.id || 'new'}
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
        <div className="space-y-6">
          {/* Active Tasks Section */}
          {activeTasks.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-700 mb-3 flex items-center">
                <span className="w-3 h-3 bg-blue-500 rounded-full mr-2"></span>
                Active Tasks ({activeTasks.length})
              </h3>
              <div className="space-y-2">
                {activeTasks.map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    onToggle={handleToggleTask}
                    onDelete={handleDeleteTask}
                    onEdit={handleEditTask}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Completed Tasks Section */}
          {completedTasks.length > 0 && (
            <div className="border-t pt-4">
              <button
                onClick={() => setShowCompleted(!showCompleted)}
                className="flex items-center text-lg font-semibold text-gray-600 mb-3 hover:text-gray-800 transition-colors"
              >
                <span className={`transform transition-transform ${showCompleted ? 'rotate-90' : ''}`}>
                  ▶
                </span>
                <span className="w-3 h-3 bg-green-500 rounded-full mx-2"></span>
                Completed Tasks ({completedTasks.length})
              </button>
              {showCompleted && (
                <div className="space-y-2 opacity-75">
                  {completedTasks.map((task) => (
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
          )}

          {/* Show message when all tasks are completed */}
          {activeTasks.length === 0 && completedTasks.length > 0 && (
            <div className="text-center py-4 bg-green-50 rounded-lg border border-green-200">
              <span className="text-green-700 font-medium">🎉 All tasks completed! Great job!</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}