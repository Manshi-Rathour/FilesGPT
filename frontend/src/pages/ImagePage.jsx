import { Image } from "lucide-react";

export default function ImagePage({ onBack, onChat }) {
  return (
    <div className="flex items-center justify-center h-screen bg-gradient-to-br from-indigo-200 via-purple-200 to-pink-200 p-6">
      <div className="bg-white rounded-xl shadow p-6 w-full max-w-md">
        <h2 className="font-bold mb-4">Upload an Image</h2>
        <button
          onClick={onChat}
          className="w-full flex items-center justify-center bg-pink-500 text-white py-2 rounded-lg mb-4 hover:bg-pink-600"
        >
          <Image className="w-4 h-4 mr-2" /> Upload Image
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
