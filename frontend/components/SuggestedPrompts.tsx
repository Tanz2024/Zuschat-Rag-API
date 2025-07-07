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
  // Popular & General
  {
    text: "What's new at ZUS Coffee this month?",
    category: "Popular",
    priority: 1,
    tags: ["new", "latest", "updates", "promotion"]
  },
  {
    text: "Find ZUS Coffee outlets near KLCC",
    category: "Popular", 
    priority: 1,
    tags: ["location", "klcc", "outlets", "nearby"]
  },
  {
    text: "Show me your best-selling drinks",
    category: "Popular",
    priority: 1,
    tags: ["drinks", "popular", "coffee", "bestseller"]
  },
  {
    text: "What promotions are available today?",
    category: "Popular",
    priority: 1,
    tags: ["promotion", "deals", "discount", "offers"]
  },

  // Calculation & Pricing
  {
    text: "Calculate total cost for 2 Cappuccino and 1 Croissant",
    category: "Calculations",
    priority: 1,
    tags: ["calculate", "cost", "total", "price", "cart"]
  },
  {
    text: "How much tax is included in a RM15.90 drink?",
    category: "Calculations",
    priority: 1,
    tags: ["tax", "gst", "sst", "calculation", "breakdown"]
  },
  {
    text: "What's the price difference between sizes?",
    category: "Calculations",
    priority: 2,
    tags: ["price", "size", "difference", "comparison", "calculate"]
  },
  {
    text: "Show me drinks priced between RM8-RM12",
    category: "Calculations",
    priority: 2,
    tags: ["price", "range", "budget", "filter", "drinks"]
  },

  // Numbers & Statistics
  {
    text: "How many ZUS Coffee outlets are in Kuala Lumpur?",
    category: "Numbers & Stats",
    priority: 1,
    tags: ["count", "outlets", "number", "kuala lumpur", "statistics"]
  },
  {
    text: "What are the top 5 most expensive drinks?",
    category: "Numbers & Stats",
    priority: 2,
    tags: ["top", "expensive", "ranking", "price", "list"]
  },
  {
    text: "How many products cost under RM10?",
    category: "Numbers & Stats",
    priority: 2,
    tags: ["count", "products", "price", "budget", "affordable"]
  },
  {
    text: "Show me 3 cheapest food items",
    category: "Numbers & Stats",
    priority: 2,
    tags: ["cheapest", "food", "budget", "ranking", "affordable"]
  },

  // Products & Pricing
  {
    text: "Show me coffee tumblers under RM40",
    category: "Products",
    priority: 2,
    tags: ["tumbler", "drinkware", "price", "budget"]
  },
  {
    text: "Calculate discount for bulk purchase of 10 drinks",
    category: "Products",
    priority: 2,
    tags: ["bulk", "discount", "calculate", "quantity", "savings"]
  },
  {
    text: "What's the total for family combo meal?",
    category: "Products",
    priority: 2,
    tags: ["family", "combo", "total", "calculate", "meal"]
  },
  {
    text: "Compare prices: Americano vs Cappuccino vs Latte",
    category: "Products",
    priority: 2,
    tags: ["compare", "price", "coffee", "americano", "cappuccino", "latte"]
  },

  // Outlet Numbers & Locations
  {
    text: "How many outlets are open 24 hours?",
    category: "Outlets",
    priority: 2,
    tags: ["count", "24hours", "outlets", "operating hours"]
  },
  {
    text: "Find 5 nearest outlets to my location",
    category: "Outlets", 
    priority: 2,
    tags: ["nearest", "location", "outlets", "proximity", "number"]
  },
  {
    text: "Which outlet has the largest seating capacity?",
    category: "Outlets",
    priority: 2,
    tags: ["seating", "capacity", "largest", "space", "number"]
  },
  {
    text: "Show outlets with drive-thru service count",
    category: "Outlets",
    priority: 2,
    tags: ["drive-thru", "count", "service", "outlets", "convenience"]
  }
]

const getHighPriorityPrompts = (): SuggestedPrompt[] => {
  // Get priority 1 prompts first (most important)
  const priority1 = SUGGESTED_PROMPTS.filter(prompt => prompt.priority === 1)
  
  // Get some priority 2 prompts to fill remaining slots
  const priority2 = SUGGESTED_PROMPTS.filter(prompt => prompt.priority === 2)
  
  // Mix categories for better variety - take top priority 1s and some priority 2s
  const mixed = [...priority1.slice(0, 6), ...priority2.slice(0, 6)]
  
  return mixed.slice(0, 12) // Return up to 12 prompts
}

interface SuggestedPromptsProps {
  onPromptClick: (prompt: string) => void
  disabled?: boolean
}

const SuggestedPrompts: React.FC<SuggestedPromptsProps> = ({ onPromptClick, disabled = false }) => {
  const prompts = getHighPriorityPrompts().slice(0, 8) // Get top 8 high-priority prompts for better variety

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
