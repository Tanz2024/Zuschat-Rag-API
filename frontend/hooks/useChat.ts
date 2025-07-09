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

// Enhanced storage utility with fallback to sessionStorage
const storageUtils = {
  setItem: (key: string, value: string) => {
    try {
      localStorage.setItem(key, value)
      // Also backup to sessionStorage
      sessionStorage.setItem(key + '_backup', value)
    } catch (e) {
      console.warn('localStorage failed, using sessionStorage:', e)
      try {
        sessionStorage.setItem(key, value)
      } catch (e2) {
        console.error('Both localStorage and sessionStorage failed:', e2)
      }
    }
  },
  
  getItem: (key: string): string | null => {
    try {
      const item = localStorage.getItem(key)
      if (item) return item
      
      // Fallback to sessionStorage
      const backup = sessionStorage.getItem(key + '_backup')
      if (backup) {
        console.log('Restored from sessionStorage backup:', key)
        return backup
      }
      
      return sessionStorage.getItem(key)
    } catch (e) {
      console.warn('Storage access failed:', e)
      return null
    }
  },
  
  removeItem: (key: string) => {
    try {
      localStorage.removeItem(key)
      sessionStorage.removeItem(key)
      sessionStorage.removeItem(key + '_backup')
    } catch (e) {
      console.warn('Storage removal failed:', e)
    }
  }
}

export const useChat = (options: UseChatOptions = {}): UseChatReturn => {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null)
  
  const { onError, onResponse } = options
  
  // Load chat history from localStorage on mount with better persistence
  useEffect(() => {
    const loadChatHistory = () => {
      try {
        const savedMessages = storageUtils.getItem('zus-chat-history')
        const savedSessionId = storageUtils.getItem('zus-chat-session-id')
        let initialMessages: ChatMessage[] = []
        
        console.log('Loading chat history from localStorage...', { savedMessages: !!savedMessages, savedSessionId })
        
        if (savedMessages && savedMessages !== 'undefined' && savedMessages !== 'null') {
          try {
            const parsed = JSON.parse(savedMessages)
            if (Array.isArray(parsed) && parsed.length > 0) {
              const messagesWithDates = parsed.map((msg: any) => ({
                ...msg,
                timestamp: new Date(msg.timestamp || Date.now())
              }))
              initialMessages = messagesWithDates
              console.log('Restored chat history:', initialMessages.length, 'messages')
              
              // Restore session ID if available
              if (savedSessionId && savedSessionId !== 'null' && savedSessionId !== 'undefined') {
                setSessionId(savedSessionId)
                console.log('Restored session ID:', savedSessionId)
              }
            }
          } catch (parseError) {
            console.error('Error parsing saved chat history:', parseError)
            // Clear corrupted data
            storageUtils.removeItem('zus-chat-history')
            storageUtils.removeItem('zus-chat-session-id')
          }
        }
        
        // Only add welcome message if no saved messages were found
        if (initialMessages.length === 0) {
          console.log('No saved messages found, creating welcome message')
          const welcomeMessage: ChatMessage = {
            id: generateId(),
            role: 'assistant',
            content: 'Hello! I\'m your ZUS Coffee assistant. I can help you with product information, outlet locations, and simple calculations. How can I assist you today?',
            timestamp: new Date(),
          }
          initialMessages = [welcomeMessage]
        }
        
        setMessages(initialMessages)
      } catch (error) {
        console.error('Error loading chat history:', error)
        // Fallback to welcome message
        const welcomeMessage: ChatMessage = {
          id: generateId(),
          role: 'assistant',
          content: 'Hello! I\'m your ZUS Coffee assistant. I can help you with product information, outlet locations, and simple calculations. How can I assist you today?',
          timestamp: new Date(),
        }
        setMessages([welcomeMessage])
      }
    }

    // Small delay to ensure localStorage is ready
    const timeoutId = setTimeout(loadChatHistory, 100)
    return () => clearTimeout(timeoutId)
  }, [])

  // Save messages to localStorage whenever they change with better persistence
  useEffect(() => {
    if (messages.length > 0) {
      try {
        // Use a more specific key to avoid conflicts
        const serializedMessages = JSON.stringify(messages)
        storageUtils.setItem('zus-chat-history', serializedMessages)
        console.log('Saved chat history to storage:', messages.length, 'messages')
        
        // Also save a timestamp for when this was last updated
        storageUtils.setItem('zus-chat-last-updated', new Date().toISOString())
      } catch (error) {
        console.error('Error saving chat history to localStorage:', error)
      }
    }
  }, [messages])

  // Save session ID whenever it changes with better persistence
  useEffect(() => {
    if (sessionId) {
      try {
        storageUtils.setItem('zus-chat-session-id', sessionId)
        console.log('Saved session ID to storage:', sessionId)
      } catch (error) {
        console.error('Error saving session ID to localStorage:', error)
      }
    }
  }, [sessionId])

  // Add localStorage health check and prevent data loss on page unload
  useEffect(() => {
    // Check localStorage health periodically
    const checkLocalStorage = () => {
      try {
        const testKey = 'zus-localStorage-test'
        localStorage.setItem(testKey, 'test')
        localStorage.removeItem(testKey)
        return true
      } catch (e) {
        console.error('localStorage not available:', e)
        return false
      }
    }

    if (!checkLocalStorage()) {
      console.warn('localStorage is not available - chat history will not persist')
      return
    }

    // Ensure data is saved before page unload
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (messages.length > 1) { // More than just welcome message
        try {
          storageUtils.setItem('zus-chat-history', JSON.stringify(messages))
          if (sessionId) {
            storageUtils.setItem('zus-chat-session-id', sessionId)
          }
          storageUtils.setItem('zus-chat-last-updated', new Date().toISOString())
          console.log('Chat data saved before page unload')
        } catch (error) {
          console.error('Error saving chat data before unload:', error)
        }
      }
    }

    // Save data on visibility change (when tab becomes hidden)
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'hidden' && messages.length > 1) {
        try {
          storageUtils.setItem('zus-chat-history', JSON.stringify(messages))
          if (sessionId) {
            storageUtils.setItem('zus-chat-session-id', sessionId)
          }
          storageUtils.setItem('zus-chat-last-updated', new Date().toISOString())
          console.log('Chat data saved on visibility change')
        } catch (error) {
          console.error('Error saving chat data on visibility change:', error)
        }
      }
    }

    window.addEventListener('beforeunload', handleBeforeUnload)
    document.addEventListener('visibilitychange', handleVisibilityChange)

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload)
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [messages, sessionId])

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
    console.log('Clearing chat - user initiated')
    
    // Clear localStorage completely with specific keys
    storageUtils.removeItem('zus-chat-history')
    storageUtils.removeItem('zus-chat-session-id')
    storageUtils.removeItem('zus-chat-last-updated')
    storageUtils.removeItem('messageFeedback') // Keep for backwards compatibility
    
    // Also clear old keys for backwards compatibility
    storageUtils.removeItem('chatHistory')
    storageUtils.removeItem('chatSessionId')
    
    // Reset all state
    setMessages([])
    setSessionId(null)
    setLastResponse(null)
    setIsLoading(false)
    setIsTyping(false)
    setError(null)
    
    // Add welcome message back after a brief delay to ensure clean state
    setTimeout(() => {
      const welcomeMessage: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        content: 'Hello! I\'m your ZUS Coffee assistant. I can help you with product information, outlet locations, and simple calculations. How can I assist you today?',
        timestamp: new Date(),
      }
      setMessages([welcomeMessage])
      console.log('Chat cleared and welcome message added')
    }, 100)
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
