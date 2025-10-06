import { Link } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Prism from '../Prism';

export default function WebsitePage() {
  const navigate = useNavigate();
  const [url, setUrl] = useState("");

  const handleSubmit = () => {
    if (!url) return alert("Please enter a website URL.");
    navigate("/chat", { state: { websiteUrl: url } });
  };

  const goBack = () => navigate("/home");

  return (
    <div className="relative w-full h-screen overflow-hidden">
      {/* Prism Background */}
      <div className="absolute inset-0 -z-10 bg-black">
        <Prism
          animationType="rotate"
          timeScale={0.5}
          height={3.5}
          baseWidth={5.5}
          scale={4.5}
          hueShift={0}
          colorFrequency={1}
          noise={0}
          glow={1}
        />
      </div>

      {/* Centered Card */}
      <div className="flex items-center justify-center h-screen p-6">
        <div className="bg-black/50 rounded-3xl shadow p-6 w-full max-w-md flex flex-col gap-4">
          <h2 className="font-bold text-white text-center text-lg">Enter Website URL</h2>

          {/* URL Input */}
          <input
            type="text"
            placeholder="Paste website link..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="px-3 py-2 rounded-lg flex-1 bg-black/20 text-white placeholder-gray-300 border border-gray-600 mb-3.5"
          />

          {/* Continue Button */}
          <button
            onClick={handleSubmit}
            className="w-full flex items-center justify-center bg-green-500 text-white py-2 rounded-lg hover:bg-green-600 transition"
          >
            <Link className="w-4 h-4 mr-2" /> Continue
          </button>

          {/* Back Button */}
          <button
            onClick={goBack}
            className="w-full mt-2 text-white border border-green-500 px-4 py-2 rounded-lg hover:bg-green-700 transition"
          >
            Back
          </button>
        </div>
      </div>
    </div>
  );
}
