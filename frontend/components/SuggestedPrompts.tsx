import React from 'react'

// EMBEDDED PROMPTS DATA - NO EXTERNAL IMPORTS TO AVOID VERCEL CACHE ISSUES
interface SuggestedPrompt {
  text: string
  category: string
  icon?: string
  priority: number
  tags: string[]
}

const SUGGESTED_PROMPTS: SuggestedPrompt[] = [
  {
    text: "What's new at ZUS Coffee this month?",
    category: "🌟 Popular",
    priority: 1,
    tags: ["new", "latest", "updates", "promotion"]
  },
  {
    text: "Find ZUS Coffee outlets near KLCC",
    category: "🌟 Popular", 
    priority: 1,
    tags: ["location", "klcc", "outlets", "nearby"]
  },
  {
    text: "Show me your best-selling drinks",
    category: "🌟 Popular",
    priority: 1,
    tags: ["drinks", "popular", "coffee", "bestseller"]
  },
  {
    text: "What promotions are available today?",
    category: "🌟 Popular",
    priority: 1,
    tags: ["promotion", "deals", "discount", "offers"]
  },
  {
    text: "Show me coffee tumblers under RM40",
    category: "☕ Products",
    priority: 2,
    tags: ["tumbler", "drinkware", "price", "budget"]
  },
  {
    text: "What drinkware collections do you have?",
    category: "☕ Products",
    priority: 2,
    tags: ["drinkware", "collection", "merchandise", "products"]
  }
]

const getHighPriorityPrompts = (): SuggestedPrompt[] => {
  return SUGGESTED_PROMPTS.filter(prompt => prompt.priority <= 2).slice(0, 8)
}

interface SuggestedPromptsProps {
  onPromptClick: (prompt: string) => void
  disabled?: boolean
}

const SuggestedPrompts: React.FC<SuggestedPromptsProps> = ({ onPromptClick, disabled = false }) => {
  const prompts = getHighPriorityPrompts().slice(0, 6) // Get top 6 high-priority prompts

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
      {prompts.map((promptObj, index) => (
        <button
          key={index}
          onClick={() => !disabled && onPromptClick(promptObj.text)}
          disabled={disabled}
          className={`p-4 text-left bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-xl hover:border-blue-300 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-gray-700 transition-all duration-200 shadow-sm hover:shadow-md ${
            disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
          }`}
          style={{
            fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
          }}
        >
          <div className="text-gray-900 dark:text-white font-medium"
               style={{
                 fontSize: '14px',
                 fontWeight: '500',
                 letterSpacing: '-0.011em',
                 lineHeight: '1.5'
               }}>
            {promptObj.text}
          </div>
          <div className="text-gray-500 dark:text-gray-400 mt-1.5"
               style={{
                 fontSize: '12px',
                 fontWeight: '400',
                 letterSpacing: '-0.008em',
                 lineHeight: '1.4'
               }}>
            {promptObj.category}
          </div>
        </button>
      ))}
    </div>
  )
}

export default SuggestedPrompts
