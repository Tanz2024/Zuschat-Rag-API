import React from 'react'
import { Menu, X } from 'lucide-react'

interface HeaderProps {
  onClearChat?: () => void
  isSidebarOpen: boolean
  onToggleSidebar: () => void
}

const Header: React.FC<HeaderProps> = ({ onClearChat, isSidebarOpen, onToggleSidebar }) => {
  return (
    <header className="bg-white dark:bg-gray-800 backdrop-blur-md border-b border-gray-200 dark:border-gray-700 shadow-sm sticky top-0 z-50 transition-colors duration-300">
      <div className="flex justify-between items-center h-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        {/* Left section */}
        <div className="flex items-center gap-6">
          {/* Enhanced Hamburger menu - ZUS Brand Style */}
          <button
            onClick={onToggleSidebar}
            className="group p-2.5 rounded-lg bg-white dark:bg-gray-700 hover:bg-blue-50 dark:hover:bg-gray-600 transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-1 shadow-sm border border-gray-300 dark:border-gray-600"
            style={{ 
              '--tw-ring-color': '#0057FF'
            } as React.CSSProperties}
            aria-label="Toggle sidebar"
            title={`${isSidebarOpen ? 'Close' : 'Open'} sidebar`}
          >
            <div className="relative w-5 h-5">
              {/* Menu icon with smooth animation */}
              <div className={`absolute inset-0 transition-all duration-200 ease-in-out ${
                isSidebarOpen ? 'opacity-0 rotate-90' : 'opacity-100 rotate-0'
              }`}>
                <Menu className="w-5 h-5 text-gray-600 dark:text-gray-300 group-hover:text-blue-600 dark:group-hover:text-blue-400" />
              </div>
              {/* X icon with smooth animation */}
              <div className={`absolute inset-0 transition-all duration-200 ease-in-out ${
                isSidebarOpen ? 'opacity-100 rotate-0' : 'opacity-0 -rotate-90'
              }`}>
                <X className="w-5 h-5 text-gray-600 dark:text-gray-300 group-hover:text-blue-600 dark:group-hover:text-blue-400" />
              </div>
            </div>
          </button>
          
          {/* ZUS Coffee Brand - Premium Typography */}
          <div className="flex items-center gap-4">
            {/* Brand Typography - Premium Modern Design */}
            <div className="hidden sm:block">
              <div className="flex items-baseline gap-3">
                <h1 className="text-2xl md:text-3xl lg:text-4xl font-black tracking-[-0.02em] leading-none uppercase select-none" 
                    style={{ 
                      color: '#0057FF',
                      fontFamily: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                      textShadow: '0 1px 2px rgba(0, 87, 255, 0.1)'
                    }}>
                  ZUS
                </h1>
                <h1 className="text-2xl md:text-3xl lg:text-4xl font-semibold tracking-[-0.01em] leading-none text-gray-900 dark:text-white select-none"
                    style={{ fontFamily: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif' }}>
                  Coffee
                </h1>
                <div className="w-1 h-1 rounded-full bg-gray-300 dark:bg-gray-600 self-center ml-1"></div>
                <span className="text-sm md:text-base lg:text-lg font-medium tracking-wide text-gray-600 dark:text-gray-400 self-center"
                      style={{ fontFamily: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif' }}>
                  AI Assistant
                </span>
              </div>
            </div>
            
            {/* Mobile brand name - Optimized for small screens */}
            <div className="block sm:hidden">
              <div className="flex items-baseline gap-2">
                <span className="text-xl font-black tracking-[-0.02em] uppercase select-none" 
                      style={{ 
                        color: '#0057FF',
                        fontFamily: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
                      }}>
                  ZUS
                </span>
                <span className="text-xl font-semibold tracking-[-0.01em] text-gray-900 dark:text-white select-none"
                      style={{ fontFamily: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif' }}>
                  Coffee
                </span>
                <div className="w-0.5 h-0.5 rounded-full bg-gray-400 dark:bg-gray-500 self-center"></div>
                <span className="text-xs font-medium text-gray-600 dark:text-gray-400 self-center"
                      style={{ fontFamily: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif' }}>
                  AI
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right section - ZUS Brand Controls */}
        <div className="flex items-center gap-4">
          {/* New Chat Button - Modern Professional Design */}
          {onClearChat && (
            <button
              onClick={onClearChat}
              className="flex items-center gap-2 px-4 py-2.5 text-white rounded-lg font-semibold text-sm tracking-wide transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-[1.02] active:scale-[0.98] border select-none"
              style={{ 
                backgroundColor: '#0057FF',
                borderColor: '#002D74',
                fontFamily: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                letterSpacing: '0.025em'
              } as React.CSSProperties}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#002D74'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#0057FF'
              }}
            >
              <span>New Chat</span>
            </button>
          )}
          
          {/* Status Indicator - Modern Clean Design */}
          <div className="flex items-center gap-2.5 bg-white/80 backdrop-blur-sm rounded-lg px-3 py-2 shadow-sm border border-gray-200 dark:border-gray-600 dark:bg-gray-800/80" 
               style={{ fontFamily: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif' }}>
            <div className="relative">
              <div className="h-2 w-2 rounded-full shadow-sm" style={{ backgroundColor: '#10B981' }}></div>
              <div className="absolute inset-0 h-2 w-2 rounded-full animate-ping opacity-30" style={{ backgroundColor: '#10B981' }}></div>
            </div>
            <span className="text-xs font-medium text-gray-700 dark:text-gray-300 tracking-wide select-none">Online</span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
