import React, { useEffect, useRef, useState, useCallback } from 'react'
import Image from 'next/image'
import MessageBubble from './MessageBubble'
import MessageInput from './MessageInput'
import TypingIndicator from './TypingIndicator'
import Toast from './Toast'
import { useChat } from '../hooks/useChat'

interface Product {
  id: string
  name: string
  price?: string
  image?: string
  description?: string
  category?: string
  availability?: boolean
}

interface ChatWindowProps {
  isSidebarOpen?: boolean
}

const ChatWindow: React.FC<ChatWindowProps> = ({ isSidebarOpen = false }) => {
  const {
    messages,
    isLoading,
    error,
    sendMessage,
    clearChat
  } = useChat()

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [toast, setToast] = useState<{
    message: string
    type: 'success' | 'error' | 'info'
    isVisible: boolean
  }>({
    message: '',
    type: 'info',
    isVisible: false
  })

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, isLoading])

  // Memoize handleClearChat to avoid dependency issues
  const handleClearChat = useCallback(() => {
    clearChat()
  }, [clearChat])

  // Auto-scroll on component mount
  useEffect(() => {
    const timer = setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
    }, 100)
    return () => clearTimeout(timer)
  }, [handleClearChat])

  // Listen for sidebar events
  useEffect(() => {
    const handleSendMessage = (event: CustomEvent) => {
      sendMessage(event.detail)
    }

    const handleClearChatEvent = () => {
      handleClearChat()
    }

    window.addEventListener('sendChatMessage', handleSendMessage as EventListener)
    window.addEventListener('clearChat', handleClearChatEvent)

    return () => {
      window.removeEventListener('sendChatMessage', handleSendMessage as EventListener)
      window.removeEventListener('clearChat', handleClearChatEvent)
    }
<<<<<<< HEAD
  }, [sendMessage, handleClearChat]) // Added handleClearChat to dependency array
=======
  }, [sendMessage, handleClearChat])
>>>>>>> 045029b (fixes)

  // Listen for sidebar events
  useEffect(() => {
    const handleSidebarPrompt = (event: CustomEvent) => {
      sendMessage(event.detail)
    }

    const handleSidebarClearChat = () => {
      handleClearChat()
    }

    window.addEventListener('sidebar-prompt-click', handleSidebarPrompt as EventListener)
    window.addEventListener('sidebar-clear-chat', handleSidebarClearChat as EventListener)

    return () => {
      window.removeEventListener('sidebar-prompt-click', handleSidebarPrompt as EventListener)
      window.removeEventListener('sidebar-clear-chat', handleSidebarClearChat as EventListener)
    }
  }, [sendMessage, handleClearChat])

  // Show error toast
  useEffect(() => {
    if (error) {
      setToast({
        message: error,
        type: 'error',
        isVisible: true
      })
    }
  }, [error])

  // Handle message feedback
  const handleFeedback = (messageId: string, feedback: 'positive' | 'negative') => {
    // Store feedback in localStorage for persistence
    const feedbackData = JSON.parse(localStorage.getItem('messageFeedback') || '{}')
    feedbackData[messageId] = feedback
    localStorage.setItem('messageFeedback', JSON.stringify(feedbackData))
    
    // Show feedback toast
    setToast({
      message: feedback === 'positive' ? 'Thanks for your feedback!' : 'We\'ll work on improving our responses.',
      type: 'success',
      isVisible: true
    })
  }

  // Handle product clicks
  const handleProductClick = (product: Product) => {
    const productMessage = `Tell me more about ${product.name}`
    sendMessage(productMessage)
  }



  return (
    <div className="chat-container bg-gray-50/50 dark:bg-gray-900/50 transition-colors duration-300">
      {/* Messages Container - Production Layout */}
      <div className={`chat-messages ${isSidebarOpen ? 'chat-messages-with-sidebar' : 'chat-messages-expanded'}`}>
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center welcome-container">
            {/* Zuss Logo Welcome */}
<<<<<<< HEAD
            <div className="relative mb-4 sm:mb-6">
              <div className="w-16 h-16 sm:w-20 sm:h-20 bg-white dark:bg-gray-800 rounded-full flex items-center justify-center shadow-lg border-2 border-gray-100 dark:border-gray-600 transition-colors duration-300">
                <Image 
=======
            <div className="relative mb-6">
              <div className="w-20 h-20 bg-white dark:bg-gray-800 rounded-full flex items-center justify-center shadow-lg border-2 border-gray-100 dark:border-gray-600 transition-colors duration-300">
                <Image
>>>>>>> 045029b (fixes)
                  src="/assets/logos/zusslogo.jpg" 
                  alt="Zuss Coffee AI" 
                  width={64}
                  height={64}
<<<<<<< HEAD
                  className="h-12 w-12 sm:h-16 sm:w-16 object-cover rounded-full"
                  priority
=======
                  className="h-16 w-16 object-cover rounded-full"
>>>>>>> 045029b (fixes)
                />
              </div>
              {/* Online indicator */}
              <div className="absolute -bottom-1 -right-1 w-5 h-5 sm:w-6 sm:h-6 bg-gradient-to-r from-emerald-400 to-emerald-500 rounded-full border-2 border-white dark:border-gray-800 shadow-sm transition-colors duration-300">
                <div className="absolute inset-1 bg-white dark:bg-gray-800 rounded-full transition-colors duration-300"></div>
                <div className="absolute inset-1.5 bg-emerald-400 rounded-full animate-pulse"></div>
              </div>
            </div>
            
            <h2 className="welcome-title text-gray-900 dark:text-white transition-colors duration-300">
              <span style={{ color: '#0057FF', fontWeight: 'bold', textTransform: 'uppercase' }}>ZUS</span>
              <span className="text-gray-800 dark:text-white" style={{ fontWeight: '500' }}> Coffee</span>
              <span className="text-gray-500 dark:text-gray-400" style={{ fontWeight: '300' }}> • AI Assistant</span>
            </h2>
            <p className="welcome-subtitle text-gray-600 dark:text-gray-300 max-w-sm sm:max-w-md leading-relaxed transition-colors duration-300">
              I&apos;m here to help you find products, locate outlets, calculate prices, or answer questions about Zuss Coffee.
            </p>
            
            {/* Quick start suggestions */}
            <div className="welcome-buttons">
              <button 
                onClick={() => sendMessage("Show me your coffee products")}
                className="welcome-button"
              >
                <div className="font-medium text-gray-900 dark:text-white text-sm sm:text-base">Browse Coffee Products</div>
                <div className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">Explore our coffee selection</div>
              </button>
              <button 
                onClick={() => sendMessage("Find ZUS Coffee outlets near me")}
                className="welcome-button"
              >
                <div className="font-medium text-gray-900 dark:text-white text-sm sm:text-base">Find Outlets</div>
                <div className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">Locate nearby stores</div>
              </button>
              <button 
                onClick={() => sendMessage("What can you help me with?")}
                className="welcome-button"
              >
                <div className="font-medium text-gray-900 dark:text-white text-sm sm:text-base">Get Help</div>
                <div className="text-xs sm:text-sm text-gray-500 dark:text-gray-400">Learn what I can do</div>
              </button>
            </div>
            
            {!isSidebarOpen && (
              <div className="mt-6 sm:mt-8 p-3 sm:p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800 transition-colors duration-300 max-w-sm sm:max-w-md">
                <p className="text-xs sm:text-sm text-blue-700 dark:text-blue-300">
                  <strong>Tip:</strong> Click the menu button to access suggested prompts and categories
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4 p-4">
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                onFeedback={handleFeedback}
                onProductClick={handleProductClick}
              />
            ))}
            
            {/* Typing indicator */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="flex gap-4">
                  {/* Zuss AI Avatar */}
                  <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-600 shadow-sm transition-colors duration-300">
<<<<<<< HEAD
                    <Image 
=======
                    <Image
>>>>>>> 045029b (fixes)
                      src="/assets/logos/zusslogo.jpg" 
                      alt="Zuss AI" 
                      width={32}
                      height={32}
                      className="h-8 w-8 object-cover rounded-full"
                    />
                  </div>
                  {/* Typing bubble */}
                  <div className="max-w-sm md:max-w-lg lg:max-w-xl">
                    <div className="chat-bubble chat-bubble-bot">
                      <TypingIndicator />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        <div ref={messagesEndRef} className="h-4" />
      </div>

      {/* Message Input - Production Style */}
      <div className="shrink-0 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 transition-colors duration-300">
        <MessageInput
          onSendMessage={sendMessage}
          isLoading={isLoading}
          showSuggestions={messages.length === 0}
        />
      </div>

      {/* Toast Notifications */}
      <Toast
        message={toast.message}
        type={toast.type}
        isVisible={toast.isVisible}
        onClose={() => setToast(prev => ({ ...prev, isVisible: false }))}
      />
    </div>
  )
}

export default ChatWindow;
