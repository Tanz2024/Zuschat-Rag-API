import React from 'react'
import Image from 'next/image'
import { Menu, X } from 'lucide-react'

interface HeaderProps {
  onClearChat?: () => void
  isSidebarOpen: boolean
  onToggleSidebar: () => void
}

const Header: React.FC<HeaderProps> = ({ onClearChat, isSidebarOpen, onToggleSidebar }) => {
  return (
    <header className="bg-white dark:bg-gray-800 backdrop-blur-md border-b border-gray-200 dark:border-gray-700 shadow-sm sticky top-0 z-50 transition-colors duration-300">
      <div className="flex justify-between items-center h-14 sm:h-16 px-3 sm:px-4 lg:px-6 max-w-7xl mx-auto">
        {/* Left section */}
        <div className="flex items-center gap-3 sm:gap-4">
          {/* Mobile hamburger menu - exactly like ChatGPT */}
          <button
            onClick={onToggleSidebar}
            className="lg:hidden flex items-center justify-center w-10 h-10 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 btn-haptic mobile-focus-ring no-long-press"
            aria-label="Toggle sidebar"
            title={`${isSidebarOpen ? 'Close' : 'Open'} sidebar`}
          >
            <div className="relative w-6 h-6">
              {/* Menu icon with smooth animation */}
              <div className={`absolute inset-0 transition-all duration-200 ease-in-out ${
                isSidebarOpen ? 'opacity-0 rotate-90' : 'opacity-100 rotate-0'
              }`}>
                <Menu className="w-6 h-6 text-gray-700 dark:text-gray-300" />
              </div>
              {/* X icon with smooth animation */}
              <div className={`absolute inset-0 transition-all duration-200 ease-in-out ${
                isSidebarOpen ? 'opacity-100 rotate-0' : 'opacity-0 -rotate-90'
              }`}>
                <X className="w-6 h-6 text-gray-700 dark:text-gray-300" />
              </div>
            </div>
          </button>

          {/* Desktop hamburger menu */}
          <button
            onClick={onToggleSidebar}
            className="hidden lg:flex group p-2 sm:p-2.5 rounded-lg bg-white dark:bg-gray-700 hover:bg-blue-50 dark:hover:bg-gray-600 transition-all duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-1 shadow-sm border border-gray-300 dark:border-gray-600"
            style={{ 
              '--tw-ring-color': '#0057FF',
              minHeight: '44px',
              minWidth: '44px'
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
          
          {/* ZUS Coffee Brand - Mobile responsive */}
          <div className="flex items-center gap-2 sm:gap-4">
            {/* Logo - Mobile optimized */}
            <div className="flex-shrink-0">
              <Image 
                src="/assets/logos/zusslogo.jpg" 
                alt="ZUS Coffee" 
                width={40}
                height={40}
                className="h-8 w-8 sm:h-10 sm:w-10 rounded-full object-cover border-2 border-gray-200 dark:border-gray-600"
                priority
              />
            </div>
            
            {/* Brand Typography - Mobile responsive */}
            <div className="flex items-baseline gap-2 sm:gap-3">
              <h1 className="text-lg sm:text-xl lg:text-2xl xl:text-3xl font-black tracking-[-0.02em] leading-none uppercase select-none" 
                  style={{ 
                    color: '#0057FF',
                    fontFamily: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                      textShadow: '0 1px 2px rgba(0, 87, 255, 0.1)'
                    }}>
                  ZUS
                </h1>
                <h1 className="text-base sm:text-lg lg:text-xl xl:text-2xl font-semibold tracking-[-0.01em] leading-none text-gray-900 dark:text-white select-none"
                    style={{ fontFamily: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif' }}>
                  Coffee
                </h1>
                <div className="hidden sm:block w-1 h-1 rounded-full bg-gray-300 dark:bg-gray-600 self-center ml-1"></div>
                <span className="hidden sm:inline text-xs sm:text-sm lg:text-base font-medium tracking-wide text-gray-600 dark:text-gray-400 self-center"
                      style={{ fontFamily: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif' }}>
                  AI Assistant
                </span>
            </div>
          </div>
        </div>

        {/* Right section - Mobile optimized */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* New Chat Button - Mobile responsive */}
          {onClearChat && (
            <button
              onClick={onClearChat}
              className="flex items-center gap-1 sm:gap-2 px-3 py-2 sm:px-4 sm:py-2.5 text-white rounded-lg font-semibold text-xs sm:text-sm tracking-wide transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-[1.02] active:scale-[0.98] border select-none"
              style={{ 
                backgroundColor: '#0057FF',
                borderColor: '#002D74',
                fontFamily: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                letterSpacing: '0.025em',
                minHeight: '40px'
              } as React.CSSProperties}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#002D74'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#0057FF'
              }}
            >
              <span className="hidden sm:inline">New Chat</span>
              <span className="sm:hidden">New</span>
            </button>
          )}
          
          {/* Status Indicator - Mobile optimized */}
          <div className="flex items-center gap-1.5 sm:gap-2.5 bg-white/80 backdrop-blur-sm rounded-lg px-2 py-1.5 sm:px-3 sm:py-2 shadow-sm border border-gray-200 dark:border-gray-600 dark:bg-gray-800/80" 
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
