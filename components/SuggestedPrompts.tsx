import React from 'react'

// Simple, clean suggestions for ZUS Coffee chatbot (production-ready)
const SUGGESTED_PROMPTS = [
  { text: "Show me ZUS OG Cup 2.0 with screw-on lid", category: "Products" },
  { text: "What's the cheapest ceramic mug available?", category: "Products" },
  { text: "Find all products under RM60", category: "Products" },
  { text: "Show me ZUS All-Can Tumbler 600ml details", category: "Products" },
  { text: "Find ZUS Coffee outlets in Kuala Lumpur", category: "Outlets" },
  { text: "Show outlets with WiFi in Selangor", category: "Outlets" },
  { text: "Find outlets near Cheras", category: "Outlets" },
  { text: "What outlets have drive-thru service?", category: "Outlets" },
  { text: "Calculate 6% SST on RM55", category: "Calculator" },
  { text: "What's the total for 2 × RM39?", category: "Calculator" },
  { text: "Calculate RM105 + RM55 + RM39", category: "Calculator" },
  { text: "What's 20% discount on RM79?", category: "Calculator" },
]

interface SuggestedPromptsProps {
  onPromptClick: (prompt: string) => void
  disabled?: boolean
}

const SuggestedPrompts: React.FC<SuggestedPromptsProps> = ({ onPromptClick, disabled = false }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
    {SUGGESTED_PROMPTS.slice(0, 8).map((promptObj, index) => (
      <button
        key={index}
        onClick={() => !disabled && onPromptClick(promptObj.text)}
        disabled={disabled}
        className={`p-4 text-left bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-xl hover:border-blue-300 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-gray-700 transition-all duration-200 shadow-sm hover:shadow-md ${
          disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
        }`}
        style={{ fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif' }}
      >
        <div className="text-gray-900 dark:text-white font-medium" style={{ fontSize: '14px', fontWeight: '500', letterSpacing: '-0.011em', lineHeight: '1.5' }}>
          {promptObj.text}
        </div>
        <div className="text-gray-500 dark:text-gray-400 mt-1.5" style={{ fontSize: '12px', fontWeight: '400', letterSpacing: '-0.008em', lineHeight: '1.4' }}>
          {promptObj.category}
        </div>
      </button>
    ))}
  </div>
)

export default SuggestedPrompts
