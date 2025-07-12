'use client'
import { useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { FiUpload, FiCheck, FiX, FiCopy } from 'react-icons/fi'

export default function FileUpload({ mode }: { mode: 'hash' | 'verify' }) {
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [storedHash, setStoredHash] = useState('')

  const { getRootProps, getInputProps } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'image/*': ['.png', '.jpg', '.jpeg']
    },
    maxFiles: 1,
    onDrop: acceptedFiles => {
      setFile(acceptedFiles[0])
      setResult(null)
    }
  })

  const handleSubmit = async () => {
    if (!file) return
    
    setIsLoading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      // Use relative path to let Next.js handle the proxy
      const endpoint = mode === 'hash' 
        ? '/api/proxy/hash'
        : '/api/proxy/verify'

      // For verification, add stored_hash if available
      if (mode === 'verify') {
        if (!storedHash) {
          throw new Error('Original hash is required for verification')
        }
        formData.append('stored_hash', storedHash)
      }

      const res = await fetch(endpoint, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json'
        }
      })

      if (!res.ok) {
        const errorText = await res.text()
        throw new Error(`Server responded with ${res.status}: ${errorText}`)
      }

      const data = await res.json()
      setResult(data)
      
      // Auto-store hash if in hash mode
      if (mode === 'hash' && data.hash) {
        setStoredHash(data.hash)
      }

    } catch (error) {
      setResult({ 
        error: 'Processing failed',
        details: error instanceof Error ? error.message : 'Unknown error',
        // Additional debug info
        debug: {
          endpoint: mode === 'hash' ? '/api/proxy/hash' : '/api/proxy/verify',
          timestamp: new Date().toISOString()
        }
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="border border-gray-800 rounded-lg p-6">
      <div {...getRootProps()} className="border-2 border-dashed border-gray-700 rounded-lg p-8 text-center cursor-pointer hover:border-gray-600 transition-colors">
        <input {...getInputProps()} />
        <FiUpload className="mx-auto text-2xl mb-2 text-gray-400" />
        <p className="text-gray-400">
          {file ? file.name : 'Drag & drop file here, or click to select'}
        </p>
      </div>

      {file && (
        <div className="mt-4 space-y-4">
          {/* Hash input for verification mode */}
          {mode === 'verify' && (
            <div className="relative">
              <input
                type="text"
                placeholder="Paste original hash"
                className="w-full p-2 bg-gray-800 text-white rounded-md pr-10"
                value={storedHash}
                onChange={(e) => setStoredHash(e.target.value)}
              />
              {storedHash && (
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(storedHash)
                    alert('Copied to clipboard!')
                  }}
                  className="absolute right-2 top-2 text-gray-400 hover:text-white"
                >
                  <FiCopy />
                </button>
              )}
            </div>
          )}

          <button
            onClick={handleSubmit}
            disabled={isLoading || (mode === 'verify' && !storedHash)}
            className="w-full bg-white text-black py-2 px-4 rounded-md font-medium disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <span className="animate-pulse">Processing...</span>
            ) : mode === 'hash' ? (
              <>
                <FiCheck /> Calculate Hash
              </>
            ) : (
              <>
                <FiX /> Verify File
              </>
            )}
          </button>

          {result && (
            <div className={`p-4 rounded-md ${result.error ? 'bg-red-900/30' : 'bg-gray-900'}`}>
              <pre className="text-sm whitespace-pre-wrap break-words">
                {JSON.stringify(result, null, 2)}
              </pre>
              {mode === 'hash' && result.hash && (
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(result.hash)
                    alert('Hash copied!')
                  }}
                  className="mt-2 flex items-center gap-1 text-xs bg-gray-700 px-2 py-1 rounded"
                >
                  <FiCopy /> Copy Hash
                </button>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}