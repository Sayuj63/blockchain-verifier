'use client'
import { useState, useEffect } from 'react'

export default function BlockchainLog() {
  const [blocks, setBlocks] = useState<any[]>([])
  const [isValid, setIsValid] = useState<boolean | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('/api/proxy/blockchain-log')
        const data = await res.json()
        setBlocks(data.blockchain || [])
        setIsValid(data.is_valid)
      } catch (error) {
        console.error('Failed to fetch blockchain log:', error)
      }
    }

    fetchData()
  }, [])

  return (
    <div className="space-y-4">
      <div className={`p-3 rounded-md ${isValid ? 'bg-green-900/30' : 'bg-red-900/30'}`}>
        Chain Status: {isValid === true ? 'Valid' : isValid === false ? 'Invalid' : 'Loading...'}
      </div>

      <div className="space-y-2">
        {blocks.map((block) => (
          <div key={block.index} className="border border-gray-800 p-4 rounded-md">
            <div className="font-mono text-sm space-y-1">
              <p>Block #{block.index}</p>
              <p>Hash: {block.hash}</p>
              <p>Operation: {block.operation}</p>
              {block.filename && <p>File: {block.filename}</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}