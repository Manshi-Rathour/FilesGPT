// ChatHistoryPage.jsx
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";

export default function ChatHistoryPage() {
  const { chatId } = useParams();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!chatId) return;

    const fetchChat = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) throw new Error("No token found");

        console.log("[DEBUG] Fetching chat history for chatId:", chatId);
        const response = await axios.get(
          `http://127.0.0.1:5000/history/${chatId}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );

        // Normalize messages
        setMessages(response.data.messages || []);
        setLoading(false);
      } catch (err) {
        console.error("[ERROR] Failed to fetch chat:", err);
        setError("Failed to load chat history");
        setLoading(false);
      }
    };

    fetchChat();
  }, [chatId]);

  if (loading) return <div className="p-6">Loading chat...</div>;
  if (error) return <div className="p-6 text-red-500">{error}</div>;

  return (
    <div className="p-6">
      <h2 className="font-bold text-xl mb-4">Chat History</h2>
      <div className="flex flex-col gap-2">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`p-3 rounded-lg ${
              msg.sender === "user" ? "bg-indigo-100 self-end" : "bg-gray-100 self-start"
            }`}
          >
            <p>{msg.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
