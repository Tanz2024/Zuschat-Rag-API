import React from 'react'

// PRACTICAL ZUS COFFEE SUGGESTIONS - REAL DATA DRIVEN (Updated 2025-07-08)
// Focus on actual products, outlets, and useful calculations
// All suggestions are validated to work with the chatbot's real capabilities
interface SuggestedPrompt {
  text: string
  category: string
  icon?: string
  priority: number
  tags: string[]
}

const SUGGESTED_PROMPTS: SuggestedPrompt[] = [
  // Product Discovery - Real ZUS Products (Based on actual product data)
  {
    text: "Show me ZUS OG Cup 2.0 with screw-on lid",
    category: "Products",
    priority: 1,
    tags: ["og cup", "screw-on", "lid", "500ml"]
  },
  {
    text: "What's the cheapest ceramic mug available?",
    category: "Products",
    priority: 1,
    tags: ["ceramic", "mug", "budget", "rm39", "cheapest"]
  },
  {
    text: "Find all products under RM60",
    category: "Products",
    priority: 1,
    tags: ["under", "rm60", "budget", "affordable"]
  },
  {
    text: "Show me ZUS All-Can Tumbler 600ml details",
    category: "Products",
    priority: 1,
    tags: ["all-can", "tumbler", "600ml", "car", "cup holder"]
  },

  // Outlet Search - Real Locations (Based on actual outlet data)
  {
    text: "Find ZUS Coffee outlets in Kuala Lumpur",
    category: "Outlets",
    priority: 1,
    tags: ["kuala lumpur", "kl", "outlets", "location"]
  },
  {
    text: "Show outlets with WiFi in Selangor",
    category: "Outlets",
    priority: 1,
    tags: ["wifi", "selangor", "internet", "work"]
  },
  {
    text: "Find outlets near Cheras",
    category: "Outlets",
    priority: 1,
    tags: ["cheras", "near", "location", "outlets"]
  },
  {
    text: "What outlets have drive-thru service?",
    category: "Outlets",
    priority: 1,
    tags: ["drive-thru", "service", "convenient", "car"]
  },

  // Practical Calculations - Real Scenarios (Customer-focused)
  {
    text: "Calculate 6% SST on RM55",
    category: "Calculator",
    priority: 1,
    tags: ["sst", "tax", "rm55", "og cup", "realistic"]
  },
  {
    text: "What's the total for 2 × RM39?",
    category: "Calculator",
    priority: 1,
    tags: ["multiply", "rm39", "ceramic", "mug", "buy1free1"]
  },
  {
    text: "Calculate RM105 + RM55 + RM39",
    category: "Calculator",
    priority: 1,
    tags: ["add", "total", "shopping", "cart", "real prices"]
  },
  {
    text: "What's 20% discount on RM79?",
    category: "Calculator",
    priority: 1,
    tags: ["discount", "20%", "rm79", "promotion", "sale"]
  },

  // Product Comparisons - Value-driven (Based on real products)
  {
    text: "Compare ZUS OG Cup vs All-Can Tumbler",
    category: "Compare",
    priority: 2,
    tags: ["og cup", "all-can", "compare", "500ml", "600ml"]
  },
  {
    text: "Show me products in Sundaze collection",
    category: "Collections",
    priority: 2,
    tags: ["sundaze", "collection", "seashell", "sand castle"]
  },
  {
    text: "Ceramic mug vs stainless steel tumbler?",
    category: "Compare",
    priority: 2,
    tags: ["ceramic", "stainless", "material", "comparison"]
  },
  {
    text: "Which products have Buy 1 Free 1 offer?",
    category: "Promotions",
    priority: 2,
    tags: ["buy1free1", "promotion", "deals", "offers"]
  },

  // Real Business Scenarios (Customer journey focused)
  {
    text: "Calculate total cost for 3 tumblers with tax",
    category: "Shopping",
    priority: 2,
    tags: ["bulk", "calculate", "tax", "business", "gift"]
  },
  {
    text: "Find outlets open 24 hours",
    category: "Timing",
    priority: 2,
    tags: ["24 hours", "late night", "always open"]
  },
  {
    text: "What's the most premium tumbler?",
    category: "Premium",
    priority: 2,
    tags: ["premium", "mountain collection", "rm79", "luxury"]
  },
  {
    text: "Show leak-proof tumblers with screw lids",
    category: "Features",
    priority: 2,
    tags: ["leak-proof", "screw", "lid", "secure", "travel"]
  }
]

const getHighPriorityPrompts = (): SuggestedPrompt[] => {
  // Get priority 1 prompts first (most practical and useful)
  const priority1 = SUGGESTED_PROMPTS.filter(prompt => prompt.priority === 1)
  
  // Get priority 2 prompts for variety
  const priority2 = SUGGESTED_PROMPTS.filter(prompt => prompt.priority === 2)
  
  // Ensure we get a good mix of categories for priority 1
  const categories = ['Products', 'Outlets', 'Calculator']
  const categorizedPriority1: SuggestedPrompt[] = []
  
  // Get 4 from each main category (Products, Outlets, Calculator)
  categories.forEach(category => {
    const categoryPrompts = priority1.filter(p => p.category === category)
    categorizedPriority1.push(...categoryPrompts.slice(0, 4))
  })
  
  // Fill remaining slots with priority 2 prompts for variety (Compare, Collections, Shopping, etc.)
  const remaining = 12 - categorizedPriority1.length
  const selectedPriority2 = priority2.slice(0, remaining)
  
  return [...categorizedPriority1, ...selectedPriority2].slice(0, 12)
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
