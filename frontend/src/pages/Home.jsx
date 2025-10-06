import { FileText, Image, Link } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import axios from "axios";
import Prism from "../Prism";

export default function Home({ user }) {
  const navigate = useNavigate();
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!user?._id) return;

    const fetchChatHistory = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) throw new Error("No token found");

        const response = await axios.get(
          `http://127.0.0.1:5000/history/user/${user._id}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );

        console.log("RAW RESPONSE from backend:", response.data);

        if (!Array.isArray(response.data)) {
          throw new Error("Unexpected response format, expected array");
        }

        // Check keys in first object
        if (response.data.length > 0) {
          console.log(
            "Keys in first chat object:",
            Object.keys(response.data[0])
          );
        }

        // Normalize backend data
        const chats = response.data.map(chat => {
          console.log("Keys in first chat object:", Object.keys(chat));
          return {
            _id: chat._id,
            user_id: chat.user_id,
            pdf_name: chat.pdf_name,
            messages: chat.messages || [],
            created_at: chat.created_at,
            title: chat.pdf_name || (chat.messages?.[0]?.text?.substring(0, 30) + "...")
          };
        });
        console.log("✅ All normalized chats:", chats);


        setChatHistory(chats);
        setLoading(false);
      } catch (err) {
        console.error("[ERROR] Failed to fetch chat history:", err);
        setError("Failed to fetch chat history");
        setLoading(false);
      }
    };

    fetchChatHistory();
  }, [user]);

  return (
    <div className="h-screen pt-[100px] px-6 pb-6">
      <div className="absolute inset-0 -z-10 bg-black">
        <Prism
          animationType="rotate"
          timeScale={0.5}
          height={3.5}
          baseWidth={5.5}
          scale={4}
          hueShift={0}
          colorFrequency={1}
          noise={0}
          glow={1}
        />
      </div>

      <div className="flex h-full gap-6">
        {/* Sidebar */}
        <div className="w-1/4 bg-white rounded-2xl shadow flex flex-col h-full overflow-hidden">
          <div className="p-4 border-b border-gray-200 sticky top-0 bg-white z-10">
            <h2 className="font-bold text-lg">Chat History</h2>
          </div>

          <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-2">
            {loading ? (
              <p className="text-gray-500 text-sm">Loading chat history...</p>
            ) : error ? (
              <p className="text-red-500 text-sm">{error}</p>
            ) : chatHistory.length === 0 ? (
              <p className="text-gray-500 text-sm">No previous chats</p>
            ) : (
              chatHistory.map((chat) => (
                <div
                  key={chat._id}
                  onClick={() => navigate(`/chat-history/${chat._id}`)}
                  className="cursor-pointer bg-gray-100 p-3 rounded-lg hover:bg-gray-200 transition flex flex-col"
                >
                  <p className="font-medium text-gray-700 truncate">
                    {chat.title}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    {chat.created_at
                      ? new Date(chat.created_at).toLocaleString()
                      : "Unknown date"}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Main */}
        <div className="flex-1 flex items-center justify-center">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl">
            <div
              onClick={() => navigate("/pdf")}
              className="cursor-pointer bg-black/50 rounded-3xl shadow p-6 flex flex-col items-center justify-center hover:shadow-lg transition"
            >
              <FileText className="w-10 h-10 mb-4 text-indigo-600" />
              <h2 className="font-semibold text-white">Ask about PDFs</h2>
            </div>

            <div
              onClick={() => navigate("/image")}
              className="cursor-pointer bg-black/50 rounded-3xl shadow p-6 flex flex-col items-center justify-center hover:shadow-lg transition"
            >
              <Image className="w-10 h-10 mb-4 text-pink-600" />
              <h2 className="font-semibold text-white">Ask about Images</h2>
            </div>

            <div
              onClick={() => navigate("/website")}
              className="cursor-pointer bg-black/50 rounded-3xl shadow p-6 flex flex-col items-center justify-center hover:shadow-lg transition"
            >
              <Link className="w-10 h-10 mb-4 text-green-600" />
              <h2 className="font-semibold text-white">Ask about Websites</h2>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
