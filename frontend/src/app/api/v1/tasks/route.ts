import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://todo-backend:8000';

async function proxyRequest(request: NextRequest) {
  const url = `${BACKEND_URL}/api/v1/tasks`;

  const headers = new Headers();
  headers.set('Content-Type', 'application/json');

  const authHeader = request.headers.get('authorization');
  if (authHeader) {
    headers.set('Authorization', authHeader);
  }

  const cookies = request.headers.get('cookie');
  if (cookies) {
    headers.set('Cookie', cookies);
  }

  const options: RequestInit = {
    method: request.method,
    headers,
  };

  if (['POST', 'PUT', 'PATCH'].includes(request.method)) {
    try {
      const body = await request.json();
      options.body = JSON.stringify(body);
    } catch {
      // No body or invalid JSON
    }
  }

  try {
    const response = await fetch(url, options);
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { detail: 'Failed to connect to backend service' },
      { status: 502 }
    );
  }
}

export async function GET(request: NextRequest) {
  return proxyRequest(request);
}

export async function POST(request: NextRequest) {
  return proxyRequest(request);
}
