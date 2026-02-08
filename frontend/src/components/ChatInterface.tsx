'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { apiCall } from '@/lib/api';

interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  createdAt: string;
}

interface ChatProps {
  initialConversationId?: number;
}

export default function ChatInterface({ initialConversationId }: ChatProps) {
  const { state: authState } = useAuth();
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<number | null>(initialConversationId || null);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  // Load conversation if initialConversationId is provided
  useEffect(() => {
    if (initialConversationId && authState.isAuthenticated) {
      loadConversation(initialConversationId);
    }
  }, [initialConversationId, authState.isAuthenticated]);

  const loadConversation = async (id: number) => {
    try {
      setIsLoading(true);
      const response = await apiCall(`/api/v1/chat/conversations/${id}`, {
        method: 'GET',
      });

      if (response.ok) {
        const data = await response.json();
        setConversationId(data.id);

        // Transform the messages to our local format
        const transformedMessages: Message[] = data.messages.map((msg: any) => ({
          id: msg.id,
          role: msg.role as 'user' | 'assistant',
          content: msg.content,
          createdAt: msg.created_at
        }));

        setMessages(transformedMessages);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to load conversation');
      }
    } catch (err) {
      setError('An error occurred while loading the conversation');
      console.error('Error loading conversation:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading || !authState.isAuthenticated) return;

    // Add user message to the chat immediately
    const userMessage: Message = {
      id: Date.now(), // Temporary ID, will be replaced by server ID
      role: 'user',
      content: inputValue,
      createdAt: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    const currentValue = inputValue;
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      // Send the message to the backend
      const response = await apiCall('/api/v1/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversation_id: conversationId || null,
          message: currentValue,
        }),
      });

      if (response.ok) {
        const data = await response.json();

        // Update conversation ID if it's the first message
        if (!conversationId) {
          setConversationId(data.conversation_id);
        }

        // Add the AI response to the chat
        const aiMessage: Message = {
          id: Date.now() + 1, // Temporary ID
          role: 'assistant',
          content: data.response,
          createdAt: new Date().toISOString(),
        };

        setMessages(prev => [...prev, aiMessage]);

        // If tasks were modified, notify the TaskList to refresh
        if (data.tool_calls && data.tool_calls.length > 0) {
          window.dispatchEvent(new CustomEvent('tasks-updated'));
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to send message');

        // Remove the user message since it failed
        setMessages(prev => prev.slice(0, -1));
      }
    } catch (err) {
      setError('An error occurred while sending the message');
      // Remove the user message since it failed
      setMessages(prev => prev.slice(0, -1));
      console.error('Error sending message:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (!authState.isAuthenticated) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <p className="text-lg text-gray-600 mb-4">Please log in to use the chat</p>
          <a
            href="/login"
            className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
          >
            Go to Login
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-white">
      <div className="flex-1 overflow-y-auto p-2 sm:p-4 space-y-3 sm:space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-500 px-4">
            <h3 className="text-base sm:text-lg font-medium text-gray-700 mb-2">
              Hi! I'm your Todo Assistant
            </h3>
            <p className="text-xs sm:text-sm mb-4">Try one of these:</p>

            <div className="flex flex-wrap gap-2 justify-center max-w-md">
              {[
                'Add a task for tomorrow',
                'Show high priority tasks',
                "What's due this week?",
              ].map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  onClick={() => setInputValue(prompt)}
                  className="px-3 py-1.5 text-sm bg-gray-100 hover:bg-indigo-100 hover:text-indigo-700 rounded-full transition-colors cursor-pointer"
                >
                  {prompt}
                </button>
              ))}
            </div>

            <p className="mt-6 text-xs text-gray-400">
              Or just ask naturally!
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] sm:max-w-[80%] rounded-lg px-3 sm:px-4 py-2 ${
                  message.role === 'user'
                    ? 'bg-indigo-500 text-white'
                    : 'bg-gray-200 text-gray-800'
                }`}
              >
                <div className="whitespace-pre-wrap text-sm sm:text-base">{message.content}</div>
                <div className={`text-xs mt-1 ${message.role === 'user' ? 'text-indigo-200' : 'text-gray-500'}`}>
                  {new Date(message.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-200 text-gray-800 rounded-lg px-3 sm:px-4 py-2 max-w-[85%] sm:max-w-[80%]">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-75"></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-150"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded m-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="border-t p-2 sm:p-3">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={isLoading}
            placeholder="Type a message..."
            className="flex-1 border border-gray-300 rounded-md px-3 py-2.5 sm:py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 min-h-[44px] sm:min-h-0"
            aria-label="Type your message"
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="bg-indigo-600 text-white rounded-md px-3 py-2.5 sm:py-2 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed min-h-[44px] min-w-[44px] sm:min-h-0 sm:min-w-0 flex items-center justify-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </form>
    </div>
  );
}