# Quickstart Guide: Full-Stack Multi-User Web Application for Todo App

**Feature**: 002-fullstack-todo-app
**Date**: 2026-01-19

## Overview
This guide provides instructions for setting up, developing, and running the full-stack todo application with authentication and data isolation.

## Prerequisites
- Node.js 18+ (for frontend development)
- Python 3.13+ (for backend development)
- PostgreSQL (or Neon Serverless PostgreSQL account)
- Docker (optional, for containerized development)
- Git

## Environment Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Environment Variables
Create `.env` files in both backend and frontend directories:

**Backend (.env)**:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/todo_app
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000
```

**Frontend (.env.local)**:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

## Database Setup

### 1. Install Database Dependencies
```bash
pip install psycopg2-binary  # or pip install asyncpg for async PostgreSQL driver
```

### 2. Run Migrations
```bash
cd backend
# If using Alembic for migrations
alembic upgrade head
```

### 3. Initialize Database
The application will automatically create tables if they don't exist on first run.

## Running the Application

### 1. Start the Backend
```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

### 2. Start the Frontend
In a new terminal:
```bash
cd frontend
npm run dev
```

### 3. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend Docs: http://localhost:8000/docs

## Key Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/logout` - Logout

### Task Management
- `GET /api/tasks` - Get current user's tasks
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/{id}` - Get a specific task
- `PUT /api/tasks/{id}` - Update a task
- `DELETE /api/tasks/{id}` - Delete a task
- `PATCH /api/tasks/{id}/complete` - Toggle task completion

## Development Commands

### Backend
```bash
# Run tests
pytest

# Format code
black .

# Check types
mypy src/

# Run with auto-reload
uvicorn src.main:app --reload
```

### Frontend
```bash
# Development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Lint code
npm run lint

# Format code
npm run format
```

## Testing

### Backend Tests
```bash
cd backend
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/unit/test_task_service.py
```

### Frontend Tests
```bash
cd frontend
# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch
```

## Deployment

### Frontend Deployment
The frontend is designed for Vercel deployment:
```bash
# Build the application
npm run build

# Deploy to Vercel
vercel deploy
```

### Backend Deployment
The backend can be deployed to platforms that support Python/FastAPI applications.

## Troubleshooting

### Common Issues
1. **Database Connection Issues**: Verify DATABASE_URL in .env is correct
2. **Authentication Problems**: Ensure BETTER_AUTH_SECRET is the same in both frontend and backend
3. **CORS Issues**: Check that frontend URL is properly configured in backend CORS settings
4. **JWT Expiration**: Tokens have a default expiration time; users will need to re-authenticate

### Environment Variables
Make sure all required environment variables are set in both frontend and backend:
- Database connection string
- JWT secret key
- API base URLs

## Skills Integration
This project uses several Claude Code skills for development:
- `sdd-workflow-enforcer` - Enforces the full SDD workflow
- `fastapi-jwt-user-context` - Handles JWT authentication patterns
- `user-isolation-enforcer` - Ensures user data isolation
- `sqlmodel-todo-task-model` - Defines SQLModel patterns
- `fastapi-todo-rest-api` - Implements REST API patterns
- `nextjs-todo-task-ui` - Provides Next.js UI patterns
- `monorepo-spec-navigation` - Guides file placement in monorepo