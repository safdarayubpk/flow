'use client';

import React from 'react';
import { AuthProvider } from '@/components/AuthProvider';
import { Toaster } from 'sonner';
import './globals.css';

// Root layout for the entire application
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        <AuthProvider>
          <div className="min-h-screen bg-gray-50">
            {children}
          </div>
          <Toaster position="top-right" richColors />
        </AuthProvider>
      </body>
    </html>
  );
}