/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/proxy/:path*',
        destination: 'https://blockchain-verifier.onrender.com/:path*',
      },
    ]
  },
  experimental: {
    turbo: {
      rules: {
        '*.css': ['postcss']
      }
    }
  }
}

module.exports = nextConfig