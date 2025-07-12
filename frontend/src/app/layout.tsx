import '../styles/globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Blockchain Verifier',
  description: 'Verify file integrity using blockchain technology',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="bg-black text-white">
      <body className={inter.className}>
        <main className="min-h-screen p-8 max-w-6xl mx-auto">
          <h1 className="text-4xl font-bold mb-8 text-center bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
            Blockchain Verifier
          </h1>
          {children}
        </main>
      </body>
    </html>
  )
}