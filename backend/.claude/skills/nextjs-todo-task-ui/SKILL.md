---
name: nextjs-todo-task-ui
description: nextjs todo component, task card tailwind, add edit todo form, todo list ui pattern, nextjs task management ui
---

# NextJS Todo Task UI

## Overview

This skill provides standardized UI patterns for Next.js Todo applications using App Router and Tailwind CSS. It enforces consistent component design, proper data fetching with JWT authentication, and follows best practices for server and client components.

## Next.js App Router Structure

### Component Hierarchy
Use Next.js App Router with server components as default:

```
app/
├── layout.tsx
├── page.tsx
├── tasks/
│   ├── page.tsx
│   ├── [id]/
│   │   └── page.tsx
│   └── new/
│       └── page.tsx
```

## Task Card Component

### Standard Task Card Design
Use Tailwind CSS classes consistently:

```tsx
// components/TaskCard.tsx
'use client';

import { useState } from 'react';

interface Task {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
}

interface TaskCardProps {
  task: Task;
  onToggle: (id: number) => void;
  onDelete: (id: number) => void;
  onEdit: (id: number) => void;
}

export default function TaskCard({ task, onToggle, onDelete, onEdit }: TaskCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="flex flex-col p-4 mb-3 bg-white shadow rounded-lg border border-gray-200">
      <div className="flex items-start gap-3">
        <input
          type="checkbox"
          checked={task.completed}
          onChange={() => onToggle(task.id)}
          className="mt-1 h-5 w-5 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
        />
        <div className="flex-1 min-w-0">
          <h3 className={`text-lg font-medium ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
            {task.title}
          </h3>
          {task.description && (
            <div className="mt-1 text-sm text-gray-500">
              {isExpanded ? task.description : `${task.description.substring(0, 100)}${task.description.length > 100 ? '...' : ''}`}
            </div>
          )}
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => onEdit(task.id)}
            className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Edit
          </button>
          <button
            onClick={() => onDelete(task.id)}
            className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            Delete
          </button>
        </div>
      </div>
      {task.description && task.description.length > 100 && (
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="mt-2 text-xs text-blue-600 hover:text-blue-800"
        >
          {isExpanded ? 'Show less' : 'Show more'}
        </button>
      )}
    </div>
  );
}
```

## Task Form Component

### Add/Edit Task Form
Consistent form design with Tailwind:

```tsx
// components/TaskForm.tsx
'use client';

import { useState } from 'react';

interface TaskFormProps {
  onSubmit: (task: { title: string; description?: string }) => void;
  onCancel: () => void;
  initialData?: { id?: number; title: string; description?: string };
}

export default function TaskForm({ onSubmit, onCancel, initialData }: TaskFormProps) {
  const [title, setTitle] = useState(initialData?.title || '');
  const [description, setDescription] = useState(initialData?.description || '');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ title, description });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-4 rounded-lg shadow mb-4">
      <div className="mb-4">
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
          Title *
        </label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
        />
      </div>
      <div className="mb-4">
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
        ></textarea>
      </div>
      <div className="flex justify-end space-x-3">
        <button
          type="button"
          onClick={onCancel}
          className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Cancel
        </button>
        <button
          type="submit"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          {initialData ? 'Update Task' : 'Add Task'}
        </button>
      </div>
    </form>
  );
}
```

## Data Fetching with JWT

### API Integration
Use fetch with JWT Authorization header:

```tsx
// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getTasks(): Promise<Task[]> {
  const token = localStorage.getItem('jwt_token');

  const response = await fetch(`${API_BASE_URL}/api/tasks`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch tasks');
  }

  return response.json();
}

export async function createTask(task: { title: string; description?: string }): Promise<Task> {
  const token = localStorage.getItem('jwt_token');

  const response = await fetch(`${API_BASE_URL}/api/tasks`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(task),
  });

  if (!response.ok) {
    throw new Error('Failed to create task');
  }

  return response.json();
}

export async function updateTask(id: number, task: { title: string; description?: string }): Promise<Task> {
  const token = localStorage.getItem('jwt_token');

  const response = await fetch(`${API_BASE_URL}/api/tasks/${id}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(task),
  });

  if (!response.ok) {
    throw new Error('Failed to update task');
  }

  return response.json();
}

export async function deleteTask(id: number): Promise<void> {
  const token = localStorage.getItem('jwt_token');

  const response = await fetch(`${API_BASE_URL}/api/tasks/${id}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to delete task');
  }
}

export async function toggleTaskCompletion(id: number): Promise<Task> {
  const token = localStorage.getItem('jwt_token');

  const response = await fetch(`${API_BASE_URL}/api/tasks/${id}/complete`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to toggle task completion');
  }

  return response.json();
}
```

## Loading and Error States

### Suspense Wrapper
Handle loading and error states properly:

```tsx
// components/TaskList.tsx
import { Suspense } from 'react';
import TaskCard from './TaskCard';
import LoadingSpinner from './LoadingSpinner';
import { getTasks } from '../lib/api';

async function TaskListContent() {
  let tasks = [];
  try {
    tasks = await getTasks();
  } catch (error) {
    return <div className="text-red-500">Failed to load tasks: {(error as Error).message}</div>;
  }

  if (tasks.length === 0) {
    return <div className="text-center py-8 text-gray-500">No tasks found</div>;
  }

  return (
    <div>
      {tasks.map((task) => (
        <TaskCard
          key={task.id}
          task={task}
          onToggle={async (id: number) => {
            // Handle toggle completion
          }}
          onDelete={async (id: number) => {
            // Handle delete task
          }}
          onEdit={async (id: number) => {
            // Handle edit task
          }}
        />
      ))}
    </div>
  );
}

export default function TaskList() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <TaskListContent />
    </Suspense>
  );
}
```

## Tailwind CSS Classes

### Consistent Styling
Use these Tailwind classes consistently:

- **Containers**: `bg-white`, `shadow`, `rounded-lg`, `border`, `border-gray-200`
- **Flexbox**: `flex`, `flex-col`, `flex-wrap`, `items-center`, `justify-between`, `gap-4`
- **Spacing**: `p-4`, `mb-4`, `mt-2`, `px-4`, `py-2`
- **Typography**: `text-lg`, `font-medium`, `text-gray-900`, `text-sm`, `text-gray-500`
- **Buttons**: `rounded-md`, `border`, `shadow-sm`, `hover:bg-gray-50`, `focus:outline-none`, `focus:ring-2`

## Component Guidelines

### Server vs Client Components
- **Server Components**: Use for initial page rendering, data fetching, static content
- **Client Components**: Use only when needed for interactivity (use 'use client' directive)

### Best Practices
- Always handle loading and error states
- Use consistent spacing and styling
- Implement proper form validation
- Follow accessibility best practices
- Use semantic HTML elements

## Validation Checklist

Before implementing any Todo UI component:
- [ ] Uses Next.js App Router structure
- [ ] Server components by default, client components only when needed
- [ ] Tailwind CSS classes are consistent
- [ ] JWT token is included in API requests
- [ ] Loading and error states are handled
- [ ] Task card includes title, description preview, checkbox, edit/delete buttons
- [ ] Forms have proper validation and submit handling
- [ ] Data fetching follows security best practices