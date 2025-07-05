import React, { useState } from 'react'
import { Trash2, Moon, Sun, Sparkles, Coffee, Search } from 'lucide-react'
import { useTheme } from '../hooks/useTheme'

// VERCEL CACHE BUSTER - BUILD: 2025-07-05-19:55:00 - VERSION 2.0.0 - NO EXTERNAL IMPORTS
// EMBEDDED PROMPTS DATA TO ELIMINATE ALL MODULE RESOLUTION ISSUES
interface SuggestedPrompt {
  text: string
  category: string
  icon?: string
  priority: number
  tags: string[]
}

const SUGGESTED_PROMPTS: SuggestedPrompt[] = [
  // High Priority - Popular Queries
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
  // Product Related
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
  },
  {
    text: "Show me eco-friendly drinkware options",
    category: "☕ Products",
    priority: 2,
    tags: ["eco", "sustainable", "environment", "green"]
  },
  {
    text: "What steel tumblers are available?",
    category: "☕ Products",
    priority: 2,
    tags: ["steel", "tumbler", "available", "metal"]
  },
  // Outlet Related
  {
    text: "ZUS Coffee outlets in KL with drive-thru",
    category: "📍 Outlets",
    priority: 2,
    tags: ["location", "drive-thru", "kuala lumpur", "convenient"]
  },
  {
    text: "Which outlets are open 24 hours?",
    category: "📍 Outlets",
    priority: 2,
    tags: ["24hours", "late night", "hours", "open"]
  },
  // Help & Information
  {
    text: "What products do you have?",
    category: "ℹ️ Help",
    priority: 2,
    tags: ["products", "available", "catalog", "what"]
  },
  {
    text: "Show me all outlet locations",
    category: "ℹ️ Help",
    priority: 2,
    tags: ["outlets", "locations", "all", "where"]
  }
]

const getPromptsByCategory = (category: string): SuggestedPrompt[] => {
  return SUGGESTED_PROMPTS.filter(prompt => prompt.category === category)
}

const getHighPriorityPrompts = (): SuggestedPrompt[] => {
  return SUGGESTED_PROMPTS.filter(prompt => prompt.priority <= 2).slice(0, 8)
}

const searchPrompts = (query: string): SuggestedPrompt[] => {
  const lowercaseQuery = query.toLowerCase()
  return SUGGESTED_PROMPTS.filter(prompt => 
    prompt.text.toLowerCase().includes(lowercaseQuery) ||
    prompt.tags.some(tag => tag.toLowerCase().includes(lowercaseQuery))
  ).sort((a, b) => a.priority - b.priority)
}

const getPromptCategories = (): string[] => {
  const categories = new Set(SUGGESTED_PROMPTS.map(prompt => prompt.category))
  return Array.from(categories)
}

interface SidebarProps {
  onClose?: () => void
}

const Sidebar: React.FC<SidebarProps> = ({ onClose }) => {
  const { theme, toggleTheme, mounted } = useTheme()
  const [showSuggestedPrompts, setShowSuggestedPrompts] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  
  const categories = getPromptCategories()
  
  const getFilteredPrompts = () => {
    if (searchQuery.trim()) {
      return searchPrompts(searchQuery)
    }
    
    if (selectedCategory === 'all') {
      return getHighPriorityPrompts()
    }
    
    return getPromptsByCategory(selectedCategory)
  }
  
  const filteredPrompts = getFilteredPrompts()
  const groupedPrompts = filteredPrompts.reduce((acc, prompt) => {
    if (!acc[prompt.category]) {
      acc[prompt.category] = []
    }
    acc[prompt.category].push(prompt)
    return acc
  }, {} as Record<string, typeof filteredPrompts>)

  const handlePromptClick = (prompt: string) => {
    // Emit custom event for the chat to handle
    const event = new CustomEvent('sendChatMessage', { detail: prompt })
    window.dispatchEvent(event)
  }

  const handleClearChat = () => {
    const event = new CustomEvent('clearChat')
    window.dispatchEvent(event)
  }

  return (
    <aside className="sidebar-container bg-gradient-to-b from-white via-blue-50 to-white dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 border-r-2 border-blue-200 dark:border-gray-700 shadow-xl transition-colors duration-300">
      {/* Header - ZUS Coffee Style with Logo */}
      <div className="p-6 border-b-2 border-blue-100 dark:border-gray-700 shrink-0 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-700">
        <div className="flex items-center gap-4">
          <div className="relative group">
            {/* ZUS Coffee Logo - Primary Location - Circular */}
            <div className="relative">
              <img 
                src="/assets/logos/zusslogo.jpg" 
                alt="ZUS Coffee" 
                className="h-16 w-16 md:h-18 md:w-18 object-cover rounded-full border-3 transition-all duration-500 ease-in-out group-hover:scale-110 filter hover:brightness-110 shadow-lg"
                style={{ borderColor: '#0057FF' }}
              />
              {/* Premium glow ring */}
              <div className="absolute inset-0 rounded-full opacity-0 group-hover:opacity-20 transition-all duration-500 blur-md scale-110" style={{ backgroundColor: '#0057FF' }}></div>
              {/* Subtle pulsing ring */}
              <div className="absolute inset-0 rounded-full border-2 opacity-0 group-hover:opacity-60 transition-all duration-500 animate-pulse" style={{ borderColor: '#0057FF' }}></div>
            </div>
            
            {/* Floating online badge */}
            <div className="absolute -top-1 -right-1 w-4 h-4 rounded-full opacity-90 animate-pulse shadow-lg" style={{ backgroundColor: '#0057FF' }}>
              <div className="absolute inset-0.5 bg-white dark:bg-gray-800 rounded-full"></div>
              <div className="absolute inset-1 rounded-full" style={{ backgroundColor: '#0057FF' }}></div>
            </div>
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-bold text-gray-800 dark:text-white">ZUS Assistant</h2>
            <p className="text-base font-medium" style={{ color: '#0057FF' }}>Brew With Love</p>
          </div>
          
          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            disabled={!mounted}
            className="p-2 rounded-lg bg-white dark:bg-gray-700 shadow-md hover:shadow-lg transition-all duration-200 border border-gray-200 dark:border-gray-600 disabled:opacity-50"
            title={mounted ? `Switch to ${theme === 'light' ? 'dark' : 'light'} mode` : 'Loading theme...'}
          >
            {!mounted ? (
              <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-300 border-t-transparent"></div>
            ) : theme === 'light' ? (
              <Moon className="h-5 w-5 text-gray-600 dark:text-gray-300" />
            ) : (
              <Sun className="h-5 w-5 text-yellow-500" />
            )}
          </button>
        </div>
      </div>

      {/* Suggested Prompts Toggle */}
      <div className="p-4 border-b border-gray-100 dark:border-gray-700">
        <button
          onClick={() => setShowSuggestedPrompts(!showSuggestedPrompts)}
          className="w-full flex items-center justify-between p-3 rounded-lg bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-700 dark:to-gray-600 hover:from-blue-100 hover:to-purple-100 dark:hover:from-gray-600 dark:hover:to-gray-500 transition-all duration-200"
        >
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-blue-600 dark:text-blue-400" />
            <span className="font-medium text-gray-800 dark:text-white">Suggested Prompts</span>
          </div>
          <div className={`transform transition-transform duration-200 ${showSuggestedPrompts ? 'rotate-180' : ''}`}>
            <svg className="h-4 w-4 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto scrollbar-hide">
        {showSuggestedPrompts ? (
          /* Suggested Prompts */
          <div className="p-4 space-y-4">
            {/* Search Bar */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search prompts..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 text-sm bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-white transition-colors duration-200"
              />
            </div>
            
            {/* Category Filter */}
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedCategory('all')}
                className={`px-3 py-1 text-xs rounded-full transition-colors duration-200 ${
                  selectedCategory === 'all'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                }`}
              >
                All
              </button>
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-3 py-1 text-xs rounded-full transition-colors duration-200 ${
                    selectedCategory === category
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>

            {/* Prompts */}
            <div className="space-y-4">
              {Object.entries(groupedPrompts).map(([category, prompts]) => (
                <div key={category} className="space-y-2">
                  <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 px-2">
                    {category}
                  </h3>
                  <div className="space-y-2">
                    {prompts.map((prompt, index) => (
                      <button
                        key={index}
                        onClick={() => handlePromptClick(prompt.text)}
                        className="w-full text-left p-3 text-sm bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 hover:bg-blue-50 dark:hover:bg-gray-700 hover:text-blue-700 dark:hover:text-blue-400 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500 transition-all duration-200 shadow-sm hover:shadow-md group"
                      >
                        <div className="flex items-start gap-2">
                          <Coffee className="h-3 w-3 opacity-60 group-hover:opacity-100 transition-opacity mt-1 flex-shrink-0" />
                          <span className="leading-tight">{prompt.text}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              ))}
              
              {filteredPrompts.length === 0 && (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  <Coffee className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No prompts found</p>
                  <p className="text-xs">Try different keywords</p>
                </div>
              )}
            </div>
          </div>
        ) : (
          /* Default Suggested Prompts */
          <div className="p-4 space-y-4">
            <div className="space-y-4">
              {Object.entries(groupedPrompts).slice(0, 3).map(([category, prompts]) => (
                <div key={category} className="space-y-2">
                  <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 px-2">
                    {category}
                  </h3>
                  <div className="space-y-2">
                    {prompts.slice(0, 3).map((prompt, index) => (
                      <button
                        key={index}
                        onClick={() => handlePromptClick(prompt.text)}
                        className="w-full text-left p-3 text-sm bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 hover:bg-blue-50 dark:hover:bg-gray-700 hover:text-blue-700 dark:hover:text-blue-400 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-500 transition-all duration-200 shadow-sm hover:shadow-md group"
                      >
                        <div className="flex items-start gap-2">
                          <Coffee className="h-3 w-3 opacity-60 group-hover:opacity-100 transition-opacity mt-1 flex-shrink-0" />
                          <span className="leading-tight">{prompt.text}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer Actions */}
      <div className="p-4 border-t border-gray-100 dark:border-gray-700 space-y-2 shrink-0">
        <button
          onClick={handleClearChat}
          className="w-full flex items-center gap-3 px-3 py-2 text-gray-600 dark:text-gray-300 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-600 dark:hover:text-red-400 rounded-md transition-all duration-200 ease-in-out"
        >
          <Trash2 className="h-4 w-4" />
          <span className="text-sm">Clear Chat</span>
        </button>
        
        <div className="text-xs text-gray-400 dark:text-gray-500 px-3 text-center">
          ZUS Coffee AI Assistant v1.0
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
