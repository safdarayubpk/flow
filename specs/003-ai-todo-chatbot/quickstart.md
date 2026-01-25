# Quickstart Guide: Phase III AI-Powered Todo Chatbot

## Overview
This guide helps you set up and run the AI-powered todo chatbot that uses OpenAI Agents SDK and MCP (Model Context Protocol) server to integrate with the todo management system.

## Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- UV package manager
- OpenAI API key
- PostgreSQL database (Neon or local)

## Backend Setup

### 1. Environment Configuration
Create a `.env` file in the `backend/` directory:
```env
DATABASE_URL="postgresql://..."
OPENAI_API_KEY="your-openai-api-key"
SECRET_KEY="your-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 2. Install Dependencies
```bash
cd backend
uv pip install -r requirements.txt
```

### 3. Run the Backend Server
```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

## Frontend Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Run the Frontend
```bash
cd frontend
npm run dev
```

## Key Features

### AI Chat Interface
- Access the chat interface at `/chat` in the frontend
- The AI assistant can help with all basic todo operations:
  - Add tasks: "Add a task to buy groceries"
  - List tasks: "Show me my pending tasks"
  - Complete tasks: "Mark task 3 as complete"
  - Delete tasks: "Delete the meeting task"
  - Update tasks: "Change task 1 to 'Call mom tonight'"

### Conversation Management
- Each user has their own conversations
- Context is maintained across multiple exchanges
- Conversations are persisted in the database

### Security & Isolation
- User authentication via JWT tokens
- Users can only access their own conversations and tasks
- MCP tools enforce user isolation at the service level

## Architecture Components

### MCP Server (`/src/mcp_server/`)
- Provides standardized tools for AI to interact with backend
- Tools: add_task, list_tasks, complete_task, delete_task, update_task
- Ensures safe, controlled access to backend services

### Chat API (`/src/api/v1/chat.py`)
- Main endpoint for chat interactions
- Manages conversation state and context
- Integrates with OpenAI Agents SDK

### Conversation Service (`/src/services/conversation_service.py`)
- Handles conversation and message persistence
- Enforces user isolation for conversations

## Environment Variables

### Backend
- `OPENAI_API_KEY`: Required for AI functionality
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT signing key
- `ENVIRONMENT`: Set to "production" for production settings

### Frontend
- `NEXT_PUBLIC_API_URL`: Backend API URL (defaults to http://localhost:8000)

## Troubleshooting

### Common Issues
1. **OpenAI API errors**: Verify `OPENAI_API_KEY` is set correctly
2. **Authentication errors**: Check JWT token handling and httpOnly cookie configuration
3. **Database connection**: Ensure `DATABASE_URL` is properly configured
4. **MCP server not responding**: Check that the MCP tools are properly registered

### Development Tips
- The chat interface will be available at http://localhost:3000/chat
- API documentation is available at http://localhost:8000/docs
- Use the `/tasks` page alongside the chat interface to see updates in real-time