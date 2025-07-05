import React, { useState, useEffect } from 'react'
import Head from 'next/head'
import Header from '../components/Header'
// import Sidebar from '../components/Sidebar' // TEMPORARILY DISABLED FOR VERCEL DEPLOYMENT
import ChatWindow from '../components/ChatWindow'

export default function Home() {
  // Use null initially to prevent hydration flicker
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean | null>(null)

  // Load sidebar preference from localStorage after mount
  useEffect(() => {
    const savedState = localStorage.getItem('sidebarOpen')
    if (savedState !== null) {
      setIsSidebarOpen(JSON.parse(savedState))
    } else {
      setIsSidebarOpen(false) // Default to closed for maximum chat space
    }
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
  if (isSidebarOpen === null) {
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
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        
        {/* Enhanced Font Loading */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet" />
        
        {/* Favicons */}
        <link rel="icon" href="/favicon-16.svg" sizes="16x16" type="image/svg+xml" />
        <link rel="icon" href="/favicon-32.svg" sizes="32x32" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.svg" sizes="180x180" />
        <link rel="icon" href="/favicon.ico" />
        
        {/* Theme and Meta */}
        <meta name="theme-color" content="#0057FF" />
        <meta name="application-name" content="ZUS Coffee AI" />
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
      
      <div className="app-layout relative">
        {/* Sidebar overlay */}
        {isSidebarOpen && (
          <div 
            className="sidebar-overlay"
            onClick={closeSidebar}
          />
        )}
        
        {/* Sidebar - TEMPORARILY DISABLED FOR VERCEL DEPLOYMENT */}
        {/* <div className={`sidebar-container ${isSidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
          <Sidebar onClose={closeSidebar} />
        </div> */}
        
        {/* Main content - expands to full width when sidebar is closed */}
        <div className={`main-layout main-layout-sidebar-closed`}>
          <div className="flex flex-col h-screen">
            <Header 
              isSidebarOpen={false}
              onToggleSidebar={() => {}}
            />
            <main className={`flex-1 overflow-hidden transition-all duration-300 ease-in-out chat-expanded`}>
              <ChatWindow isSidebarOpen={isSidebarOpen} />
            </main>
          </div>
        </div>
      </div>
    </>
  )
}
