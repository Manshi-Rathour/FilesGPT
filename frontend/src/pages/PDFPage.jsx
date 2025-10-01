import { FileText, Link } from "lucide-react";

export default function PDFPage({ onBack, onChat }) {
  return (
    <div className="flex items-center justify-center h-screen bg-gradient-to-br from-indigo-200 via-purple-200 to-pink-200 p-6">
      <div className="bg-white rounded-xl shadow p-6 w-full max-w-md">
        <h2 className="font-bold mb-4">Upload or Link a PDF</h2>
        <button
          onClick={onChat}
          className="w-full flex items-center justify-center bg-indigo-500 text-white py-2 rounded-lg mb-4 hover:bg-indigo-600"
        >
          <FileText className="w-4 h-4 mr-2" /> Upload PDF
        </button>
        <div className="flex gap-2">
          <input placeholder="Paste PDF link..." className="px-3 py-2 border rounded-lg flex-1" />
          <button onClick={onChat} className="px-4 py-2 bg-indigo-500 text-white rounded-lg">
            <Link className="w-4 h-4" />
          </button>
        </div>
        <button onClick={onBack} className="w-full mt-4 border px-4 py-2 rounded-lg">
          Back
        </button>
      </div>
    </div>
  );
}
