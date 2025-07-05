// Suggested prompts for ZUS Coffee chatbot
// Note: This file is kept for compatibility but the actual data is embedded in components

export interface SuggestedPrompt {
  text: string
  category: string
  icon?: string
  priority: number
  tags: string[]
}

export const SUGGESTED_PROMPTS: SuggestedPrompt[] = [
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

export const getHighPriorityPrompts = (): SuggestedPrompt[] => {
  return SUGGESTED_PROMPTS.filter(prompt => prompt.priority <= 2).slice(0, 8)
}

export default SUGGESTED_PROMPTS