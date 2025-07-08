import React, { useState, useEffect } from 'react'
import Head from 'next/head'
import Header from '../components/Header'
import Sidebar from '../components/Sidebar'
import ChatWindow from '../components/ChatWindow'

export default function Home() {
  // Use null initially to prevent hydration flicker
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean | null>(null)
  const [isLayoutReady, setIsLayoutReady] = useState(false)

  // Load sidebar preference from localStorage after mount
  useEffect(() => {
    const savedState = localStorage.getItem('sidebarOpen')
    if (savedState !== null) {
      setIsSidebarOpen(JSON.parse(savedState))
    } else {
      setIsSidebarOpen(false) // Default to closed for maximum chat space
    }
    
    // Small delay to prevent layout shift
    setTimeout(() => {
      setIsLayoutReady(true)
    }, 100)
  }, [])

  // Save sidebar state to localStorage
  useEffect(() => {
    if (isSidebarOpen !== null) {
      localStorage.setItem('sidebarOpen', JSON.stringify(isSidebarOpen))
    }
  }, [isSidebarOpen])

  // Handle sidebar toggle
  const toggleSidebar = () => {
    setIsSidebarOpen(prev => !prev)
  }

  // Close sidebar when clicking outside
  const closeSidebar = () => {
    setIsSidebarOpen(false)
  }

  // Handle keyboard shortcuts (YouTube style: Ctrl+B)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isSidebarOpen) {
        setIsSidebarOpen(false)
      }
      // Toggle sidebar with Ctrl/Cmd + B (like YouTube)
      if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault()
        toggleSidebar()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isSidebarOpen])

  // Show loading state to prevent layout flicker
  if (isSidebarOpen === null || !isLayoutReady) {
    return (
      <div className="flex h-screen bg-gray-50 dark:bg-gray-900 items-center justify-center transition-colors duration-300">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-3 text-gray-600 dark:text-gray-300">
          Loading <span style={{ color: '#0057FF', fontWeight: 'bold' }}>ZUS</span>
          <span className="text-gray-800 dark:text-white"> Coffee</span>
          <span style={{ color: '#8A94A6' }}> • AI Assistant</span>...
        </span>
      </div>
    )
  }

  return (
    <>
      <Head>
        <title>ZUS Coffee • AI Assistant</title>
        <meta name="description" content="Get instant answers about ZUS Coffee outlets, products, and services with our AI assistant. Find nearby outlets, discover menu items, and calculate your orders." />
<<<<<<< HEAD
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover" />
=======
        <meta name="viewport" content="width=device-width, initial-scale=1" />
>>>>>>> 045029b (fixes)
        
        {/* Favicons */}
        <link rel="icon" href="/favicon-16.svg" sizes="16x16" type="image/svg+xml" />
        <link rel="icon" href="/favicon-32.svg" sizes="32x32" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.svg" sizes="180x180" />
        <link rel="icon" href="/favicon.ico" />
        
        {/* Theme and Meta */}
        <meta name="theme-color" content="#0057FF" />
        <meta name="apple-mobile-web-app-title" content="ZUS Coffee AI" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        
        {/* Open Graph */}
        <meta property="og:title" content="ZUS Coffee • AI Assistant" />
        <meta property="og:description" content="Get instant answers about ZUS Coffee outlets, products, and services" />
        <meta property="og:image" content="/apple-touch-icon.svg" />
        <meta property="og:type" content="website" />
        <meta property="og:locale" content="en_MY" />
        
        {/* Twitter */}
        <meta name="twitter:card" content="summary" />
        <meta name="twitter:title" content="ZUS Coffee • AI Assistant" />
        <meta name="twitter:description" content="Your Perfect Cup Assistant" />
        <meta name="twitter:image" content="/apple-touch-icon.svg" />
        
        {/* Performance and Security */}
        <meta httpEquiv="X-DNS-Prefetch-Control" content="on" />
        <meta name="referrer" content="origin-when-cross-origin" />
      </Head>
      
      <div className={`app-layout relative ${isLayoutReady ? '' : 'loading'}`}>
        {/* Sidebar overlay - Works on both mobile and desktop */}
        {isSidebarOpen && (
          <div 
            className="sidebar-overlay"
            onClick={closeSidebar}
            onTouchStart={closeSidebar} // Better mobile touch support
          />
        )}
        
        {/* Sidebar - Mobile responsive */}
        <div className={`sidebar-container ${isSidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
          <Sidebar onClose={closeSidebar} />
        </div>
        
        {/* Main content - Mobile first responsive */}
        <div 
          className={`main-layout ${typeof window !== 'undefined' && isSidebarOpen && window.innerWidth >= 1024 ? 'main-layout-sidebar-open' : 'main-layout-sidebar-closed'}`}
          onClick={isSidebarOpen ? closeSidebar : undefined} // Close sidebar when clicking main content
        >
          <div className="flex flex-col h-full">
            <Header 
              isSidebarOpen={isSidebarOpen}
              onToggleSidebar={toggleSidebar}
            />
            <main className={`flex-1 overflow-hidden transition-all duration-300 ease-in-out ${isSidebarOpen ? 'chat-sidebar-open' : 'chat-expanded'}`}>
              <ChatWindow isSidebarOpen={isSidebarOpen} />
            </main>
          </div>
        </div>
      </div>
    </>
  )
}
