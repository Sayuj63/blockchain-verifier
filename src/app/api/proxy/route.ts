import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  const apiUrl = 'https://blockchain-verifier.onrender.com'
  const path = new URL(request.url).pathname.replace('/api/proxy', '')
  
  console.log(`Proxying to: ${apiUrl}${path}`) // Debug log

  try {
    const formData = await request.formData()
    const response = await fetch(`${apiUrl}${path}`, {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      const error = await response.text()
      throw new Error(`Backend error: ${error}`)
    }

    return response
  } catch (error) {
    console.error('Proxy error:', error)
    return NextResponse.json(
      { error: 'Failed to process file' },
      { status: 500 }
    )
  }
}