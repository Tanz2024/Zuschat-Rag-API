import { useState, useCallback, useRef, useEffect } from 'react'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  products?: any[]
  feedback?: 'positive' | 'negative' | null
}

export interface ChatResponse {
  message: string
  timestamp: string
}

export interface UseChatOptions {
  onError?: (error: string) => void
  onResponse?: (response: ChatResponse) => void
}

export interface UseChatReturn {
  messages: ChatMessage[]
  isLoading: boolean
  isTyping: boolean
  error: string | null
  sessionId: string | null
  sendMessage: (message: string) => Promise<void>
  clearChat: () => void
  lastResponse: ChatResponse | null
}

// Generate unique ID for messages
const generateId = () => Math.random().toString(36).substr(2, 9)

export const useChat = (options: UseChatOptions = {}): UseChatReturn => {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null)
  
  const { onError, onResponse } = options
  
  // Load chat history from localStorage on mount
  useEffect(() => {
    const savedMessages = localStorage.getItem('chatHistory')
    if (savedMessages) {
      try {
        const parsed = JSON.parse(savedMessages)
        const messagesWithDates = parsed.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }))
        setMessages(messagesWithDates)
      } catch (error) {
        console.error('Error loading chat history:', error)
      }
    }
    
    if (messages.length === 0) {
      // Initialize with welcome message
      const welcomeMessage: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        content: 'Hello! I\'m your ZUS Coffee assistant. I can help you with product information, outlet locations, and simple calculations. How can I assist you today?',
        timestamp: new Date(),
      }
      setMessages([welcomeMessage])
    }
  }, [])

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('chatHistory', JSON.stringify(messages))
    }
  }, [messages])

  const sendMessage = useCallback(async (messageContent: string) => {
    if (!messageContent.trim() || isLoading) return

    // Clear any previous errors
    setError(null)

    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: messageContent.trim(),
      timestamp: new Date(),
    }

    // Add user message immediately
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setIsTyping(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: messageContent.trim() }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data: ChatResponse = await response.json()

      // Simulate typing delay for better UX
      setTimeout(() => {
        const assistantMessage: ChatMessage = {
          id: generateId(),
          role: 'assistant',
          content: data.message,
          timestamp: new Date(),
        }

        setMessages(prev => [...prev, assistantMessage])
        setLastResponse(data)
        setIsTyping(false)
        
        // Call response callback
        onResponse?.(data)
      }, 500)

    } catch (error) {
      setIsTyping(false)
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred'
      setError(errorMessage)
      
      const errorAssistantMessage: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        content: `I'm sorry, I encountered an error: ${errorMessage}. Please try again.`,
        timestamp: new Date(),
      }

      setMessages(prev => [...prev, errorAssistantMessage])
      onError?.(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }, [isLoading, sessionId, onError, onResponse])

  const clearChat = useCallback(() => {
    setMessages([])
    setSessionId(null)
    setLastResponse(null)
    setIsLoading(false)
    setIsTyping(false)
    setError(null)
    
    // Clear localStorage
    localStorage.removeItem('chatHistory')
    localStorage.removeItem('messageFeedback')
    
    // Add welcome message back
    const welcomeMessage: ChatMessage = {
      id: generateId(),
      role: 'assistant',
      content: 'Hello! I\'m your ZUS Coffee assistant. I can help you with product information, outlet locations, and simple calculations. How can I assist you today?',
      timestamp: new Date(),
    }
    setMessages([welcomeMessage])
  }, [])

  return {
    messages,
    isLoading,
    isTyping,
    error,
    sessionId,
    sendMessage,
    clearChat,
    lastResponse,
  }
}
