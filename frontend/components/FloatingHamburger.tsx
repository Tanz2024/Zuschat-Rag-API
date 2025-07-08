import React from 'react'
import { Menu, X } from 'lucide-react'

interface FloatingHamburgerProps {
  isSidebarOpen: boolean
  onToggleSidebar: () => void
}

const FloatingHamburger: React.FC<FloatingHamburgerProps> = ({ 
  isSidebarOpen, 
  onToggleSidebar 
}) => {
  return (
    <button
      onClick={onToggleSidebar}
      className="floating-hamburger lg:hidden no-select"
      style={{ 
        background: isSidebarOpen 
          ? 'rgba(239, 68, 68, 0.95)' 
          : 'rgba(255, 255, 255, 0.95)',
        borderColor: isSidebarOpen 
          ? 'rgba(239, 68, 68, 0.3)' 
          : 'rgba(0, 0, 0, 0.08)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)'
      }}
      aria-label={isSidebarOpen ? 'Close menu' : 'Open menu'}
      title={isSidebarOpen ? 'Close menu' : 'Open menu'}
      role="button"
      tabIndex={0}
    >
      <div className="relative w-6 h-6 flex items-center justify-center">
        {/* Menu icon */}
        <div className={`absolute inset-0 transition-all duration-300 ease-in-out flex items-center justify-center ${
          isSidebarOpen ? 'opacity-0 rotate-180 scale-50' : 'opacity-100 rotate-0 scale-100'
        }`}>
          <Menu className="w-6 h-6 text-gray-700" />
        </div>
        {/* X icon */}
        <div className={`absolute inset-0 transition-all duration-300 ease-in-out flex items-center justify-center ${
          isSidebarOpen ? 'opacity-100 rotate-0 scale-100' : 'opacity-0 -rotate-180 scale-50'
        }`}>
          <X className="w-6 h-6 text-white" />
        </div>
      </div>
    </button>
  )
}

export default FloatingHamburger
