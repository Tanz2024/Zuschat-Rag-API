import React, { useState, useRef, useEffect } from 'react'
import { Send, Loader2 } from 'lucide-react'
import SuggestedPrompts from './SuggestedPrompts'

interface MessageInputProps {
  onSendMessage: (message: string) => Promise<void>
  isLoading?: boolean
  isDisabled?: boolean
  placeholder?: string
  showSuggestions?: boolean
}

const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  isLoading = false,
  isDisabled = false,
  placeholder = "Ask me about ZUS Coffee products, outlets, or anything else...",
  showSuggestions = true
}) => {
  const [message, setMessage] = useState('')
  const [isFocused, setIsFocused] = useState(false)
  const [isMounted, setIsMounted] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  
  const isInputDisabled = isDisabled || isLoading

  // Handle mounting state to prevent flash of content
  useEffect(() => {
    // Increased delay to coordinate with ChatWindow and prevent "Try asking:" from flashing on page load
    const timer = setTimeout(() => {
      setIsMounted(true)
    }, 250) // Slightly longer than ChatWindow delay
    
    return () => clearTimeout(timer)
  }, [])

  // Handle keyboard visibility for mobile
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const currentContainer = containerRef.current;
    
    // Simple keyboard detection
    const handleFocusIn = () => {
      if (currentContainer) {
        currentContainer.classList.add('keyboard-visible');
        document.body.classList.add('keyboard-open');
      }
    };
    
    const handleFocusOut = () => {
      setTimeout(() => {
        if (currentContainer) {
          currentContainer.classList.remove('keyboard-visible');
          document.body.classList.remove('keyboard-open');
        }
      }, 100);
    };
    
    // Listen for focus events on input elements
    document.addEventListener('focusin', handleFocusIn);
    document.addEventListener('focusout', handleFocusOut);
    
    return () => {
      document.removeEventListener('focusin', handleFocusIn);
      document.removeEventListener('focusout', handleFocusOut);
      
      if (currentContainer) {
        currentContainer.classList.remove('keyboard-visible');
      }
      document.body.classList.remove('keyboard-open');
    };
  }, [])

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`
    }
  }, [message])

  // Scroll input into view when focused on mobile
  const handleFocus = () => {
    setIsFocused(true)
    
    // Add focus class to body for mobile styling
    document.body.classList.add('input-focused');
    
    // Simple mobile focus handling
    if (window.innerWidth <= 768 && textareaRef.current) {
      setTimeout(() => {
        textareaRef.current?.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'center'
        });
      }, 100);
    }
  }

  const handleBlur = (e: React.FocusEvent) => {
    // Don't blur if clicking on the send button
    if (e.relatedTarget && 
        e.relatedTarget instanceof HTMLButtonElement && 
        e.relatedTarget.type === 'submit') {
      return
    }
    
    setIsFocused(false)
    document.body.classList.remove('input-focused');
    
    if (containerRef.current) {
      containerRef.current.classList.remove('keyboard-visible')
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && !isInputDisabled) {
      onSendMessage(message.trim())
      setMessage('')
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleQuickSend = (prompt: string) => {
    if (!isInputDisabled) {
      onSendMessage(prompt)
    }
  }

  return (
    <div ref={containerRef} className="chat-input-container">
      {/* Suggested Prompts - Only show after component is mounted and no messages */}
      {isMounted && showSuggestions && message.length === 0 && !isFocused && (
        <div className="mb-4 sm:mb-6 animate-mobile-fade">
          <p className="text-gray-600 dark:text-gray-300 mb-3 sm:mb-4 transition-colors duration-300 select-none text-sm sm:text-base"
             style={{ 
               fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
               fontWeight: '500',
               letterSpacing: '-0.011em',
               lineHeight: '1.5'
             }}>
            Try asking:
          </p>
          <SuggestedPrompts 
            onPromptClick={handleQuickSend}
            disabled={isInputDisabled}
          />
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={handleFocus}
            onBlur={handleBlur}
            placeholder={placeholder}
            disabled={isInputDisabled}
            rows={1}
            className={`chat-input scrollbar-hide resize-none ${isInputDisabled ? 'chat-input-disabled' : ''}`}
            style={{ 
              minHeight: '48px', 
              maxHeight: '120px',
              fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
              fontSize: '16px', // Prevent zoom on iOS
              fontWeight: '400',
              letterSpacing: '-0.011em',
              lineHeight: '1.6'
            }}
            autoComplete="off"
            autoCapitalize="sentences"
            autoCorrect="on"
            spellCheck="true"
            inputMode="text"
            enterKeyHint="send"
          />
          
          {/* GPT-style Send Button */}
          <button
            type="submit"
            disabled={!message.trim() || isInputDisabled}
            className="absolute right-2 sm:right-3 top-1/2 transform -translate-y-1/2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 disabled:bg-gray-100 dark:disabled:bg-gray-700 disabled:opacity-50 text-gray-600 dark:text-gray-300 disabled:text-gray-400 w-8 h-8 sm:w-10 sm:h-10 rounded-full transition-all duration-200 ease-in-out flex items-center justify-center mobile-touch-target btn-haptic mobile-focus-ring"
            style={{
              backgroundColor: !message.trim() || isInputDisabled ? undefined : '#0084ff',
              color: !message.trim() || isInputDisabled ? undefined : 'white',
              minHeight: '44px', // iOS minimum touch target
              minWidth: '44px',
              touchAction: 'manipulation', // Prevent double-tap zoom
              WebkitTapHighlightColor: 'transparent' // Remove iOS tap highlight
            }}
            onMouseDown={(e) => {
              // Prevent input blur when clicking send button
              e.preventDefault()
            }}
            onTouchStart={(e) => {
              // Prevent scroll on button touch and add visual feedback
              e.currentTarget.style.transform = 'translateY(-50%) scale(0.95)'
              // Don't prevent default here to allow the touch to proceed to click
            }}
            onTouchEnd={(e) => {
              // Restore button scale
              e.currentTarget.style.transform = 'translateY(-50%) scale(1)'
            }}
            onTouchCancel={(e) => {
              // Restore button scale if touch is cancelled
              e.currentTarget.style.transform = 'translateY(-50%) scale(1)'
            }}
            onClick={(e) => {
              // Handle the click directly and prevent any blur interference
              e.preventDefault()
              e.stopPropagation()
              if (message.trim() && !isInputDisabled) {
                handleSubmit(e)
              }
            }}
            aria-label="Send message"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 animate-spin" />
            ) : (
              <Send className="w-4 h-4 sm:w-5 sm:h-5" />
            )}
          </button>
        </div>
      </form>
    </div>
  )
}

export default MessageInput
