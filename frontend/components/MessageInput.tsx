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
  const [isKeyboardVisible, setIsKeyboardVisible] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  
  const isInputDisabled = isDisabled || isLoading

  // Handle keyboard visibility for mobile
  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    let initialHeight = window.innerHeight;
    let timeoutId: NodeJS.Timeout;
    
    // Capture current ref value for cleanup
    const containerElement = containerRef.current;
    
    const handleResize = () => {
      const currentHeight = window.innerHeight;
      const heightDifference = initialHeight - currentHeight;
      const keyboardVisible = heightDifference > 100; // Lower threshold for better detection
      
      setIsKeyboardVisible(keyboardVisible);
      
      // Adjust container position when keyboard is visible
      if (containerRef.current) {
        if (keyboardVisible) {
          containerRef.current.classList.add('keyboard-visible');
          document.body.classList.add('keyboard-open');
        } else {
          containerRef.current.classList.remove('keyboard-visible');
          document.body.classList.remove('keyboard-open');
        }
      }
    }

    const handleVisualViewport = () => {
      if (window.visualViewport) {
        const keyboardVisible = window.visualViewport.height < window.innerHeight * 0.75;
        setIsKeyboardVisible(keyboardVisible);
        
        if (containerRef.current) {
          if (keyboardVisible) {
            containerRef.current.classList.add('keyboard-visible');
            document.body.classList.add('keyboard-open');
          } else {
            containerRef.current.classList.remove('keyboard-visible');
            document.body.classList.remove('keyboard-open');
          }
        }
      }
    }

    // Use visual viewport API if available (better for modern browsers)
    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', handleVisualViewport);
    } else {
      // Fallback to window resize
      window.addEventListener('resize', handleResize);
    }

    // Handle orientation change
    const handleOrientationChange = () => {
      timeoutId = setTimeout(() => {
        initialHeight = window.innerHeight;
        handleResize();
      }, 500);
    };

    window.addEventListener('orientationchange', handleOrientationChange);

    return () => {
      if (timeoutId) clearTimeout(timeoutId);
      if (window.visualViewport) {
        window.visualViewport.removeEventListener('resize', handleVisualViewport);
      } else {
        window.removeEventListener('resize', handleResize);
      }
      window.removeEventListener('orientationchange', handleOrientationChange);
      
      // Cleanup classes using captured ref value
      if (containerElement) {
        containerElement.classList.remove('keyboard-visible');
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
    
    // Ensure input stays visible on mobile
    setTimeout(() => {
      if (textareaRef.current && window.innerWidth <= 768) {
        textareaRef.current.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'center',
          inline: 'nearest'
        });
      }
    }, 300); // Delay to allow keyboard animation
  }

  const handleBlur = () => {
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
      {/* Suggested Prompts */}
      {showSuggestions && message.length === 0 && !isFocused && !isKeyboardVisible && (
        <div className="mb-4 sm:mb-6">
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
          />
          
          {/* Send Button */}
          <button
            type="submit"
            disabled={!message.trim() || isInputDisabled}
            className="btn-send mobile-touch-target btn-haptic mobile-focus-ring"
            aria-label="Send message"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </form>
    </div>
  )
}

export default MessageInput
