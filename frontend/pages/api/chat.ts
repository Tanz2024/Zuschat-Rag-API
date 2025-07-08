import type { NextApiRequest, NextApiResponse } from 'next'

interface BackendResponse {
  message?: string;
  response?: string;
  answer?: string;
  error?: string;
  details?: string;
  detail?: string;
  intent?: string;
  confidence?: number;
  session_id?: string;
}

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

    let data: BackendResponse | null = null;
    let backendError: string | null = null;
    try {
      data = await response.json();
    } catch {
      backendError = `Backend returned non-JSON response: ${response.status}`;
    }
    
    if (!response.ok) {
      return res.status(response.status).json({
        error: backendError || data?.error || `Backend responded with status: ${response.status}`,
        details: data?.details || data?.detail || null,
        backend_status: response.status
      });
    }
    
    // Return the response from FastAPI
    res.status(200).json({
      message: data?.message || data?.response || data?.answer || 'No response from backend',
      timestamp: new Date().toISOString(),
      intent: data?.intent || null,
      confidence: data?.confidence || null,
      session_id: data?.session_id || req.headers['x-session-id'] || 'default-session'
    });
    
  } catch (error) {
    console.error('Chat API error:', error)
    res.status(500).json({ 
      error: 'Failed to process message',
      details: error instanceof Error ? error.message : 'Unknown error'
    })
  }
}
