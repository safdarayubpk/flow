import React, { useState, useEffect } from 'react';
import TaskCard from './TaskCard';
import TaskForm from './TaskForm';
import SearchBar from './SearchBar';
import FilterPanel from './FilterPanel';
import SortDropdown from './SortDropdown';
import { apiCall } from '@/lib/api';
import { toast } from 'sonner';

// Define the Task type
type Task = {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
  user_id: string;
  priority?: 'high' | 'medium' | 'low' | null;
  tags?: string[];
  due_date?: string;
  recurrence_rule?: string;
  reminder_enabled: boolean;
};

interface FilterOptions {
  priority?: string | null;
  tags?: string[];
  dueDateBefore?: Date | null;
  recurring?: boolean | null;
}

interface TaskListProps {
  userId: string;
}

export default function TaskList({ userId }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  // State for search and filter
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<FilterOptions>({});
  const [sortBy, setSortBy] = useState<'priority' | 'due_date' | 'title' | 'created_at'>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

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

  const handleSortChange = (newSortBy: 'priority' | 'due_date' | 'title' | 'created_at') => {
    // If clicking the same sort field, toggle the order
    if (sortBy === newSortBy) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(newSortBy);
      setSortOrder('desc'); // Default to descending for new sorts
    }
    fetchTasks();
  };

  const fetchTasks = async () => {
    try {
      setLoading(true);

      // Build query parameters from filters and search
      const queryParams = new URLSearchParams();

      if (filters.priority) queryParams.append('priority', filters.priority);
      if (filters.tags && filters.tags.length > 0) {
        filters.tags.forEach(tag => queryParams.append('tags', tag));
      }
      if (filters.dueDateBefore) queryParams.append('due_date_before', filters.dueDateBefore.toISOString());
      if (filters.recurring !== null && filters.recurring !== undefined) {
        queryParams.append('recurring', filters.recurring.toString());
      }
      if (searchQuery) queryParams.append('search', searchQuery);
      if (sortBy) queryParams.append('sort', sortBy);
      queryParams.append('order', sortOrder); // Add sort order parameter

      queryParams.append('skip', '0');
      queryParams.append('limit', '100');

      const queryString = queryParams.toString();
      const url = `/api/v1/tasks${queryString ? '?' + queryString : ''}`;

      const response = await apiCall(url, {
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

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    fetchTasks();
  };

  const handleFilterChange = (newFilters: FilterOptions) => {
    setFilters(newFilters);
    fetchTasks();
  };

  const handleCreateTask = () => {
    setEditingTask(null);
    setShowForm(true);
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
        toast.success(updatedTask.completed ? 'Task completed' : 'Task reopened');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to update task');
        toast.error('Failed to update task');
      }
    } catch (err) {
      setError('An error occurred while updating the task');
      toast.error('An error occurred while updating the task');
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
        toast.success('Task deleted');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to delete task');
        toast.error('Failed to delete task');
      }
    } catch (err) {
      setError('An error occurred while deleting the task');
      toast.error('An error occurred while deleting the task');
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

  const handleSubmitTask = async (taskData: {
  id?: number;
  title: string;
  description?: string;
  priority?: 'high' | 'medium' | 'low' | null;
  tags?: string[];
  due_date?: string;
  recurrence_rule?: string;
  reminder_enabled?: boolean;
}) => {
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
            priority: taskData.priority,
            tags: taskData.tags,
            due_date: taskData.due_date,
            recurrence_rule: taskData.recurrence_rule,
            reminder_enabled: taskData.reminder_enabled,
          }),
        });
      } else {
        // Create new task
        response = await apiCall('/api/v1/tasks', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            title: taskData.title,
            description: taskData.description,
            priority: taskData.priority,
            tags: taskData.tags,
            due_date: taskData.due_date,
            recurrence_rule: taskData.recurrence_rule,
            reminder_enabled: taskData.reminder_enabled,
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
          toast.success('Task updated');
        } else {
          // Add new task to the list
          setTasks([newTask, ...tasks]);
          toast.success('Task created');
        }

        // Close the form
        setShowForm(false);
        setEditingTask(null);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to save task');
        toast.error(errorData.detail || 'Failed to save task');
      }
    } catch (err) {
      setError('An error occurred while saving the task');
      toast.error('An error occurred while saving the task');
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
      {/* Search and Filter Section */}
      <div className="mb-6 space-y-4">
        <SearchBar onSearch={handleSearch} placeholder="Search tasks..." />
        <FilterPanel
          filters={filters}
          onFilterChange={handleFilterChange}
          availableTags={Array.from(new Set(tasks.flatMap(task => task.tags || [])))}
        />
      </div>

      {/* Header with Add Task button and Sort Dropdown */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-6">
        <h2 className="text-lg sm:text-xl font-bold text-gray-800">
          Your Tasks
          <span className="block sm:inline sm:ml-2 text-sm font-normal text-gray-500">
            ({activeTasks.length} active, {completedTasks.length} completed)
          </span>
        </h2>
        <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
          <SortDropdown
            sortOption={sortBy}
            sortOrder={sortOrder}
            onSortChange={handleSortChange}
            className="mb-2 sm:mb-0 sm:mr-2"
          />
          <button
            onClick={() => {
              setEditingTask(null);
              setShowForm(true);
            }}
            className="inline-flex items-center px-4 py-2.5 sm:py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 min-h-[44px] sm:min-h-0 w-full sm:w-auto justify-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Task
          </button>
        </div>
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
              <span className="text-green-700 font-medium">All tasks completed! Great job!</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
