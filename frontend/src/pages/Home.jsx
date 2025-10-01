import { FileText, Image, Link } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="h-screen bg-gradient-to-br from-indigo-200 via-purple-200 to-pink-200 pt-[80px] px-6 pb-6">
      <div className="flex h-full gap-6">
        {/* Sidebar */}
        <div className="w-1/4 bg-white rounded-2xl shadow p-4 flex flex-col gap-4 h-full overflow-y-auto">
          <h2 className="font-bold text-lg">Chat History</h2>
          <p className="text-sm text-gray-600">No previous chats</p>
          {/* Example long content */}
          {/* <div className="space-y-2">
            {Array.from({ length: 90 }).map((_, i) => (
              <p key={i} className="text-gray-700 text-sm">Chat {i + 1}</p>
            ))}
          </div> */}
        </div>

        {/* Main Selection */}
        <div className="flex-1 flex items-center justify-center">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl">
            <div
              onClick={() => navigate("/pdf")}
              className="cursor-pointer bg-white rounded-xl shadow p-6 flex flex-col items-center justify-center hover:shadow-lg transition"
            >
              <FileText className="w-10 h-10 mb-4 text-indigo-600" />
              <h2 className="font-semibold">Ask about PDFs</h2>
            </div>

            <div
              onClick={() => navigate("/image")}
              className="cursor-pointer bg-white rounded-xl shadow p-6 flex flex-col items-center justify-center hover:shadow-lg transition"
            >
              <Image className="w-10 h-10 mb-4 text-pink-600" />
              <h2 className="font-semibold">Ask about Images</h2>
            </div>

            <div
              onClick={() => navigate("/website")}
              className="cursor-pointer bg-white rounded-xl shadow p-6 flex flex-col items-center justify-center hover:shadow-lg transition"
            >
              <Link className="w-10 h-10 mb-4 text-green-600" />
              <h2 className="font-semibold">Ask about Websites</h2>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
