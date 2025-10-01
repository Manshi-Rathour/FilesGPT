import { Link } from "lucide-react";

export default function WebsitePage({ onBack, onChat }) {
  return (
    <div className="flex items-center justify-center h-screen bg-gradient-to-br from-indigo-200 via-purple-200 to-pink-200 p-6">
      <div className="bg-white rounded-xl shadow p-6 w-full max-w-md">
        <h2 className="font-bold mb-4">Enter Website URL</h2>
        <input
          placeholder="Paste website link..."
          className="w-full px-3 py-2 border rounded-lg mb-4"
        />
        <button
          onClick={onChat}
          className="w-full flex items-center justify-center bg-green-500 text-white py-2 rounded-lg mb-4 hover:bg-green-600"
        >
          <Link className="w-4 h-4 mr-2" /> Continue
        </button>
        <button
          onClick={onBack}
          className="w-full mt-4 border px-4 py-2 rounded-lg"
        >
          Back
        </button>
      </div>
    </div>
  );
}
