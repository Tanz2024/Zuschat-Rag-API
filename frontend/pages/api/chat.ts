import type { NextApiRequest, NextApiResponse } from 'next'

// API endpoint to proxy requests to FastAPI backend
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  try {
    const { message } = req.body
    
    if (!message || typeof message !== 'string') {
      return res.status(400).json({ error: 'Message is required' })
    }

    // Get the backend URL from environment variable or use production default
    const backendUrl = process.env.BACKEND_URL || 'https://zuschat-rag-api.onrender.com'
    
    // Send request to FastAPI backend
    const response = await fetch(`${backendUrl}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        message: message,
        session_id: req.headers['x-session-id'] || 'default-session'
      }),
    })

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const data = await response.json()
    
    // Return the response from FastAPI
    res.status(200).json({
      message: data.message || data.response || data.answer || 'No response from backend',
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error('Chat API error:', error)
    res.status(500).json({ 
      error: 'Failed to process message',
      details: error instanceof Error ? error.message : 'Unknown error'
    })
  }
}
