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
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  
  const isInputDisabled = isDisabled || isLoading

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`
    }
  }, [message])

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
    <div className="chat-input-container">
      {/* Suggested Prompts */}
      {showSuggestions && message.length === 0 && !isFocused && (
        <div className="mb-6">
          <p className="text-gray-600 dark:text-gray-300 mb-4 transition-colors duration-300 select-none"
             style={{ 
               fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
               fontSize: '14px',
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
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder={placeholder}
            disabled={isInputDisabled}
            rows={1}
            className={`chat-input scrollbar-hide resize-none ${isInputDisabled ? 'chat-input-disabled' : ''}`}
            style={{ 
              minHeight: '52px', 
              maxHeight: '120px',
              fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
              fontSize: '15px',
              fontWeight: '400',
              letterSpacing: '-0.011em',
              lineHeight: '1.6'
            }}
          />
          
          {/* Send Button */}
          <button
            type="submit"
            disabled={!message.trim() || isInputDisabled}
            className="btn-send mobile-touch-target"
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

export default MessageInput;
