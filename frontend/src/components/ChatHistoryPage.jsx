import { useState, useRef, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom"; 
import ChatMessage from "../components/ChatMessage";
import axios from "axios";
import Prism from "../Prism";

export default function ChatHistoryPage() {
  const navigate = useNavigate();
  const { chatId } = useParams();
  const [messages, setMessages] = useState([]);
  const [pdfName, setPdfName] = useState("your PDF");
  const [loading, setLoading] = useState(true);
  const chatEndRef = useRef(null);

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

        console.log("[DEBUG] Chat response:", response.data);
        setMessages(response.data.messages || []);
        setPdfName(response.data.pdf_name || "your PDF");
        setLoading(false);
      } catch (err) {
        console.error("[ERROR] Failed to fetch chat:", err);
        setMessages([{ sender: "bot", text: "Failed to load chat history." }]);
        setLoading(false);
      }
    };

    fetchChat();
  }, [chatId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (loading) return <div className="p-6">Loading chat...</div>;

  return (
    <div className="relative flex flex-col h-screen  p-6 pt-[100px]">
      {/* Animated Background */}
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
      {/* Chat Box */}
      <div className="flex-1 bg-black/50 rounded-xl shadow flex flex-col p-4 overflow-y-auto max-h-[70vh]">
        <h2 className="font-bold text-white text-xl mb-4">{pdfName}</h2>
        {messages.map((m, idx) => (
          <ChatMessage key={idx} sender={m.sender} text={m.text} />
        ))}
        <div ref={chatEndRef}></div>
      </div>

      {/* Go Home Button */}
      <button
        onClick={() => navigate("/home")}
        className="w-full mt-2 text-black bg-black/50 border border-sky-600 px-4 py-2 rounded-lg hover:bg-sky-700 transition cursor-pointer"
      >
        Go to Home Page
      </button>
    </div>
  );
}
