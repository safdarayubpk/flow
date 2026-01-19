# Full-Stack Multi-User Web Application for Todo App

A secure, multi-user todo application with JWT-based authentication, PostgreSQL persistence, and strict user data isolation. The application follows Next.js/TypeScript frontend with FastAPI/SQLModel backend.

## Features

- User authentication and registration
- Secure JWT-based authentication
- Multi-user isolation (users can only see their own tasks)
- Full CRUD operations for todo tasks
- Responsive UI with Tailwind CSS
- PostgreSQL database with SQLModel ORM

## Tech Stack

- **Frontend**: Next.js 16+, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.13+
- **Database**: PostgreSQL with SQLModel ORM
- **Authentication**: Better Auth with JWT tokens
- **Deployment**: Vercel (frontend), Docker-ready (backend)

## Setup Instructions

### Prerequisites

- Node.js 18+
- Python 3.13+
- PostgreSQL (or Neon Serverless PostgreSQL account)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the environment file and configure your settings:
   ```bash
   cp .env.example .env
   ```

   Edit the `.env` file to include your database URL and auth secret.

5. Run the application:
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Copy the environment file and configure your settings:
   ```bash
   cp .env.example .env.local
   ```

   Edit the `.env.local` file to match your backend configuration.

4. Run the development server:
   ```bash
   npm run dev
   ```

## API Endpoints

The application provides the following API endpoints:

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/tasks` - Get current user's tasks
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/{id}` - Get a specific task
- `PUT /api/tasks/{id}` - Update a task
- `DELETE /api/tasks/{id}` - Delete a task
- `PATCH /api/tasks/{id}/complete` - Toggle task completion status

## Security Features

- JWT tokens stored in httpOnly cookies for XSS protection
- User data isolation through user_id filtering
- Input validation and sanitization
- Secure password hashing
- Proper authentication and authorization on all endpoints

## Development

The project follows a monorepo structure with separate frontend and backend directories. Each component can be developed and deployed independently while maintaining clear separation of concerns.

## Architecture Decisions

This project follows several key architectural decisions documented as ADRs:

- ADR-001: JWT Token Storage Method for Secure Web Application
- ADR-002: Application-Level User Isolation Pattern
- ADR-003: Soft Delete Strategy for Task Management

## License

MIT