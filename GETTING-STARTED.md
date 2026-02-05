# Todo App - Getting Started Guide

A simple guide to run your Todo application on Kubernetes (Minikube).

## Prerequisites

Make sure you have these installed:
- Docker Desktop
- Minikube
- kubectl

## Quick Commands

| Action | Command |
|--------|---------|
| Start app | `./start-app.sh` |
| Stop app | `./stop-app.sh` |
| Check status | `./status-app.sh` |

## Step-by-Step Instructions

### Starting the Application

1. **Open Terminal**

2. **Go to your project folder**
   ```bash
   cd /home/safdarayub/Desktop/claude/Hackathon/flow
   ```

3. **Start the application**
   ```bash
   ./start-app.sh
   ```

   Wait for it to complete. The browser will open automatically with your app.

### Stopping the Application

When you're done using the app:
```bash
./stop-app.sh
```

### Checking Status

To see if everything is running:
```bash
./status-app.sh
```

## Troubleshooting

### Docker is not running
- Open Docker Desktop first, then run `./start-app.sh` again

### Pods are not starting
- Run `./status-app.sh` to check the current state
- Try stopping and starting again:
  ```bash
  ./stop-app.sh
  ./start-app.sh
  ```

### Browser didn't open
- Run this command to get the URL:
  ```bash
  minikube service todo-frontend
  ```

### Need to rebuild images
- Delete minikube and start fresh:
  ```bash
  minikube delete
  ./start-app.sh
  ```

## Useful Commands

| Command | Description |
|---------|-------------|
| `kubectl get pods` | See all running pods |
| `kubectl get svc` | See all services |
| `kubectl logs -l app.kubernetes.io/name=todo-backend` | View backend logs |
| `kubectl logs -l app.kubernetes.io/name=todo-frontend` | View frontend logs |
| `minikube dashboard` | Open Kubernetes dashboard |

## App Features

- **User Authentication**: Sign up and login
- **Task Management**: Create, edit, complete, and delete tasks
- **AI Chatbot**: Ask questions about your tasks (uses Groq API)

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   Minikube                       │
│  ┌─────────────────┐    ┌─────────────────┐     │
│  │    Frontend     │───▶│    Backend      │     │
│  │   (Next.js)     │    │   (FastAPI)     │     │
│  │   Port: 3000    │    │   Port: 8000    │     │
│  └─────────────────┘    └────────┬────────┘     │
│                                  │              │
└──────────────────────────────────┼──────────────┘
                                   │
                                   ▼
                         ┌─────────────────┐
                         │ Neon PostgreSQL │
                         │   (External)    │
                         └─────────────────┘
```

## Need Help?

- Check the status: `./status-app.sh`
- View logs: `kubectl logs <pod-name>`
- Restart everything: `./stop-app.sh` then `./start-app.sh`
