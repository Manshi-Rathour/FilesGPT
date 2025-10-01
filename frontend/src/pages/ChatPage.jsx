import { useState, useRef, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom"; 
import ChatMessage from "../components/ChatMessage";
import axios from "axios";

export default function ChatPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const pdfName = location.state?.pdfName || "your PDF";

  const [messages, setMessages] = useState([
    { sender: "bot", text: `Ask your query related to "${pdfName}".` },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input;
    setMessages([...messages, { sender: "user", text: userMessage }]);
    setInput("");
    setLoading(true);

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/query/",
        {
          question: userMessage,
          top_k: 5,
        }
      );

      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: response.data.answer },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text:
            "Error: " +
            (error?.response?.data?.detail || error.message),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Save chat to backend and go home
  const saveAndGoHome = async () => {
    try {
      const token = localStorage.getItem("token");
      await axios.post(
        "http://127.0.0.1:5000/chat/save/",
        { messages },
        { headers: { Authorization: `Bearer ${token}` } }
      );

    } catch (error) {
      console.error("Failed to save chat:", error);
    } finally {
      navigate("/home");
    }
  };


  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-indigo-200 via-purple-200 to-pink-200 p-6 pt-[100px]">
      {/* Chat Box */}
      <div className="flex-1 bg-white rounded-xl shadow flex flex-col p-4 overflow-y-auto max-h-[70vh]">
        {messages.map((m, idx) => (
          <ChatMessage key={idx} sender={m.sender} text={m.text} />
        ))}
        <div ref={chatEndRef}></div>
      </div>

      {/* Input Area */}
      <div className="mt-4 flex gap-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 px-4 py-2 border rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-indigo-400"
          placeholder="Ask something..."
          rows={2}
          disabled={loading}
        />
        <button
          onClick={handleSend}
          className={`px-6 py-2 rounded-xl text-white transition ${loading
            ? "bg-gray-400 cursor-not-allowed"
            : "bg-indigo-500 hover:bg-indigo-600"
            }`}
          disabled={loading}
        >
          {loading ? "Thinking..." : "Send"}
        </button>
      </div>

      {/* Go Home Button */}
      <button
        onClick={saveAndGoHome}
        className="mt-4 w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-xl hover:bg-gray-200 transition"
      >
        Go to Home Page
      </button>
    </div>
  );
}
