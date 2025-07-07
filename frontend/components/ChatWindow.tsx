import React, { useEffect, useRef, useState } from 'react'
import MessageBubble from './MessageBubble'
import MessageInput from './MessageInput'
import TypingIndicator from './TypingIndicator'
import Toast from './Toast'
import { useChat } from '../hooks/useChat'

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

  // Auto-scroll on component mount
  useEffect(() => {
    const timer = setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
    }, 100)
    return () => clearTimeout(timer)
  }, [])

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
  }, [sendMessage])

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
  }, [sendMessage])

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
  const handleProductClick = (product: any) => {
    const productMessage = `Tell me more about ${product.name}`
    sendMessage(productMessage)
  }

  // Handle clear chat
  const handleClearChat = () => {
    clearChat()
    setToast({
      message: 'Chat history cleared',
      type: 'info',
      isVisible: true
    })
  }

  return (
    <div className="chat-container bg-gray-50/50 dark:bg-gray-900/50 transition-colors duration-300">
      {/* Messages Container - Production Layout */}
      <div className={`chat-messages ${isSidebarOpen ? 'chat-messages-with-sidebar' : 'chat-messages-expanded'}`}>
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-6 sm:p-8">
            {/* Zuss Logo Welcome */}
            <div className="relative mb-6">
              <div className="w-20 h-20 bg-white dark:bg-gray-800 rounded-full flex items-center justify-center shadow-lg border-2 border-gray-100 dark:border-gray-600 transition-colors duration-300">
                <img 
                  src="/assets/logos/zusslogo.jpg" 
                  alt="Zuss Coffee AI" 
                  className="h-16 w-16 object-cover rounded-full"
                />
              </div>
              {/* Online indicator */}
              <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-gradient-to-r from-emerald-400 to-emerald-500 rounded-full border-2 border-white dark:border-gray-800 shadow-sm transition-colors duration-300">
                <div className="absolute inset-1 bg-white dark:bg-gray-800 rounded-full transition-colors duration-300"></div>
                <div className="absolute inset-1.5 bg-emerald-400 rounded-full animate-pulse"></div>
              </div>
            </div>
            
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-3 transition-colors duration-300">
              <span style={{ color: '#0057FF', fontWeight: 'bold', textTransform: 'uppercase' }}>ZUS</span>
              <span className="text-gray-800 dark:text-white" style={{ fontWeight: '500' }}> Coffee</span>
              <span className="text-gray-500 dark:text-gray-400" style={{ fontWeight: '300' }}> • AI Assistant</span>
            </h2>
            <p className="text-lg sm:text-xl text-gray-600 dark:text-gray-300 max-w-md leading-relaxed mb-6 transition-colors duration-300">
              I'm here to help you find products, locate outlets, calculate prices, or answer questions about Zuss Coffee.
            </p>
            
            {/* Quick start suggestions */}
            <div className="grid gap-3 w-full max-w-md">
              <button 
                onClick={() => sendMessage("Show me your coffee products")}
                className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500 hover:shadow-md transition-all duration-200 text-left"
              >
                <div className="font-medium text-gray-900 dark:text-white">Browse Coffee Products</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">Explore our coffee selection</div>
              </button>
              <button 
                onClick={() => sendMessage("Find ZUS Coffee outlets near me")}
                className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500 hover:shadow-md transition-all duration-200 text-left"
              >
                <div className="font-medium text-gray-900 dark:text-white">Find Outlets</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">Locate nearby stores</div>
              </button>
              <button 
                onClick={() => sendMessage("What can you help me with?")}
                className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500 hover:shadow-md transition-all duration-200 text-left"
              >
                <div className="font-medium text-gray-900 dark:text-white">Get Help</div>
                <div className="text-sm text-gray-500 dark:text-gray-400">Learn what I can do</div>
              </button>
            </div>
            
            {!isSidebarOpen && (
              <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800 transition-colors duration-300">
                <p className="text-sm text-blue-700 dark:text-blue-300">
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
                    <img 
                      src="/assets/logos/zusslogo.jpg" 
                      alt="Zuss AI" 
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
