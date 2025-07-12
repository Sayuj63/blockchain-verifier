import BlockchainLog from '../components/BlockchainLog'

export default function VerifyPage() {
  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-semibold">Blockchain Audit Log</h2>
      <BlockchainLog />
    </div>
  )
}