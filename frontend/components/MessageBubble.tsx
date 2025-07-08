import React, { useState } from 'react'
import Image from 'next/image'
import ProductCard from './ProductCard'
import { User, ThumbsUp, ThumbsDown } from 'lucide-react'

export interface ChatMessage {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  products?: Product[]
  feedback?: 'positive' | 'negative' | null
}

interface Product {
  id: string
  name: string
  price?: string
  image?: string
  description?: string
  category?: string
  availability?: boolean
}

interface MessageBubbleProps {
  message: ChatMessage
  isTyping?: boolean
  onFeedback?: (messageId: string, feedback: 'positive' | 'negative') => void
  onProductClick?: (product: Product) => void
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ 
  message, 
  isTyping = false,
  onFeedback,
  onProductClick 
}) => {
  const [localFeedback, setLocalFeedback] = useState<'positive' | 'negative' | null>(
    message.feedback || null
  )
  
  const isUser = message.role === 'user'

  const handleFeedback = (feedback: 'positive' | 'negative') => {
    const newFeedback = localFeedback === feedback ? null : feedback
    setLocalFeedback(newFeedback)
    if (newFeedback) {
      onFeedback?.(message.id, newFeedback)
    }
  }

  const renderContent = () => {
    // Check if content contains structured data (like product results)
    if (message.content.includes('```json') && !isUser) {
      try {
        const jsonMatch = message.content.match(/```json\n([\s\S]*?)\n```/)
        if (jsonMatch) {
          const data = JSON.parse(jsonMatch[1])
          if (data.products && Array.isArray(data.products)) {
            return (
              <div className="space-y-3">
                <p className="mobile-text-optimized">{message.content.replace(/```json[\s\S]*?```/, '').trim()}</p>
                <div className="product-grid">
                  {data.products.map((product: Product, index: number) => (
                    <ProductCard
                      key={index}
                      product={product}
                      onClick={onProductClick}
                    />
                  ))}
                </div>
              </div>
            )
          }
        }
      } catch {
        // Fall back to regular text display
      }
    }

    // Regular text content with modern typography - Mobile optimized
    return (
      <div className="whitespace-pre-wrap break-words message-content"
           style={{
             fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
             fontSize: isUser ? '14px' : '14px',
             fontWeight: isUser ? '500' : '400',
             letterSpacing: '-0.011em',
             lineHeight: '1.6',
             fontFeatureSettings: '"cv02", "cv03", "cv04", "cv11"'
           }}>
        {message.content}
      </div>
    )
  }

  return (
    <div className={`flex gap-3 sm:gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'} slide-up group mobile-chat-spacing`}>
      {/* Avatar - Mobile responsive */}
      <div className={`flex-shrink-0 message-avatar rounded-full flex items-center justify-center transition-colors duration-300 ${
        isUser ? 'bg-gradient-to-r from-blue-500 to-blue-600' : 'bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-600 shadow-sm'
      }`}>
        {isUser ? (
          <User className="h-4 w-4 sm:h-5 sm:w-5 text-white" />
        ) : (
          <Image 
            src="/assets/logos/zusslogo.jpg" 
            alt="Zuss AI" 
            width={32}
            height={32}
            className="h-6 w-6 sm:h-8 sm:w-8 object-cover rounded-full"
          />
        )}
      </div>

      {/* Message Content - Mobile responsive */}
      <div className={`flex-1 ${isUser ? 'max-w-xs sm:max-w-sm md:max-w-lg lg:max-w-xl' : 'max-w-xs sm:max-w-sm md:max-w-lg lg:max-w-xl'}`}>
        <div className={`chat-bubble ${isUser ? 'chat-bubble-user' : 'chat-bubble-bot'}`}>
          {isTyping ? (
            <div className="flex items-center gap-1">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
              <span className="text-gray-500 ml-2 select-none"
                    style={{
                      fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                      fontSize: '14px',
                      fontWeight: '400',
                      letterSpacing: '-0.011em',
                      lineHeight: '1.5',
                      fontStyle: 'italic'
                    }}>
                ZUS AI is thinking...
              </span>
            </div>
          ) : (
            <>
              {renderContent()}
              
              {/* Product cards for bot messages with products */}
              {message.products && message.products.length > 0 && (
                <div className="product-grid mt-3">
                  {message.products.map((product, index) => (
                    <ProductCard
                      key={index}
                      product={product}
                      onClick={onProductClick}
                    />
                  ))}
                </div>
              )}
            </>
          )}
        </div>
        
        {/* Timestamp and feedback */}
        <div className={`flex items-center justify-between mt-1 ${
          isUser ? 'flex-row-reverse' : 'flex-row'
        }`}>
          {/* Timestamp */}
          {message.timestamp && !isTyping && (
            <div className="text-gray-400 font-medium select-none"
                 style={{
                   fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                   fontSize: '12px',
                   fontWeight: '500',
                   letterSpacing: '-0.008em',
                   lineHeight: '1.4'
                 }}>
              {new Date(message.timestamp).toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </div>
          )}
          
          {/* Feedback buttons for bot messages */}
          {!isUser && !isTyping && (
            <div className="feedback-buttons">
              <button
                onClick={() => handleFeedback('positive')}
                className={`feedback-btn mobile-touch-target ${
                  localFeedback === 'positive' ? 'active-positive' : ''
                }`}
                title="Helpful response"
              >
                <ThumbsUp className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleFeedback('negative')}
                className={`feedback-btn mobile-touch-target ${
                  localFeedback === 'negative' ? 'active-negative' : ''
                }`}
                title="Not helpful"
              >
                <ThumbsDown className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default MessageBubble
