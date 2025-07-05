import React from 'react'

export default function TestPage() {
  return (
    <div style={{ 
      fontFamily: 'Arial, sans-serif', 
      maxWidth: '800px', 
      margin: '50px auto', 
      padding: '20px' 
    }}>
      <div style={{ 
        background: '#0057FF', 
        color: 'white', 
        padding: '20px', 
        borderRadius: '8px', 
        marginBottom: '20px' 
      }}>
        <h1>🚀 ZUS Coffee Chatbot - Minimal Test</h1>
        <p>This page should deploy successfully on Vercel</p>
      </div>
      
      <div style={{ 
        background: '#f0f8ff', 
        padding: '15px', 
        borderRadius: '8px', 
        borderLeft: '4px solid #0057FF' 
      }}>
        <h3>✅ Status</h3>
        <p><strong>Next.js:</strong> Working</p>
        <p><strong>TypeScript:</strong> Working</p>
        <p><strong>Vercel:</strong> Should be working now</p>
        <p><strong>Date:</strong> July 5, 2025</p>
      </div>
    </div>
  )
}
