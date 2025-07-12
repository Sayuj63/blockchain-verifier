# Blockchain Document Verifier

A modern web application for verifying document authenticity using blockchain technology. This frontend is built with Next.js and connects to a blockchain-based verification backend.

## Features

- 📄 Upload documents to generate unique hashes
- 🔍 Verify document authenticity against stored hashes
- 🔗 Copy hashes with a single click
- 📱 Responsive design that works on all devices
- ⚡ Fast and efficient with Next.js 14

## Getting Started

### Prerequisites

- Node.js 18 or later
- npm or yarn

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Sayuj63/blockchain-verifier.git
   cd blockchain-verifier
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn
   ```

3. Start the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## How It Works

1. **Hash Generation**: Upload a document to generate a unique cryptographic hash
2. **Verification**: Verify a document's authenticity by comparing its hash with the stored value
3. **Security**: All operations are performed securely in the browser

## Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **State Management**: React Hooks
- **UI Components**: Custom components with React Icons
- **API**: Next.js API Routes with proxy configuration

## Configuration

The application is pre-configured to work with the default backend. If you need to change the backend URL, update the `next.config.js` file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
