import dynamic from 'next/dynamic';

const FileUpload = dynamic(
  () => import('@/app/components/FileUpload'),
  { ssr: false }
)

export default function Home() {
  return (
    <div className="space-y-12">
      <section className="text-center">
        <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
          Upload files to calculate hashes or verify their integrity against the blockchain
        </p>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <FileUpload mode="hash" />
        <FileUpload mode="verify" />
      </div>
    </div>
  )
}