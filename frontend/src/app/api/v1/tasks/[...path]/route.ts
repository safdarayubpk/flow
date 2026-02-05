import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://todo-backend:8000';

async function proxyRequest(request: NextRequest, path: string[]) {
  const queryString = request.nextUrl.search;
  const url = `${BACKEND_URL}/api/v1/tasks/${path.join('/')}${queryString}`;

  const headers = new Headers();
  headers.set('Content-Type', 'application/json');

  // Forward authorization header if present
  const authHeader = request.headers.get('authorization');
  if (authHeader) {
    headers.set('Authorization', authHeader);
  }

  // Forward cookies if present
  const cookies = request.headers.get('cookie');
  if (cookies) {
    headers.set('Cookie', cookies);
  }

  const options: RequestInit = {
    method: request.method,
    headers,
  };

  // Add body for POST, PUT, PATCH requests
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

    // Handle 204 No Content (e.g. DELETE responses)
    if (response.status === 204) {
      return new NextResponse(null, { status: 204 });
    }

    const data = await response.json();

    const nextResponse = NextResponse.json(data, { status: response.status });

    const setCookie = response.headers.get('set-cookie');
    if (setCookie) {
      nextResponse.headers.set('Set-Cookie', setCookie);
    }

    return nextResponse;
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { detail: 'Failed to connect to backend service' },
      { status: 502 }
    );
  }
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  return proxyRequest(request, path);
}
