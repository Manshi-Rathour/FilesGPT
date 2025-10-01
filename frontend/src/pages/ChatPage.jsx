import { useState } from "react";
import ChatMessage from "../components/ChatMessage";

export default function ChatPage({ onBack }) {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Upload a file or link to start chatting." },
  ]);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages([...messages, { sender: "user", text: input }]);
    setInput("");

    setTimeout(() => {
      setMessages((prev) => [...prev, { sender: "bot", text: "Mock: " + input }]);
    }, 500);
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-indigo-200 via-purple-200 to-pink-200 p-6">
      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        <div className="bg-white rounded-xl shadow flex-1 p-4 overflow-y-auto space-y-3">
          {messages.map((m, idx) => (
            <ChatMessage key={idx} sender={m.sender} text={m.text} />
          ))}
        </div>
        <div className="flex gap-2 mt-4">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 px-3 py-2 border rounded-lg resize-none"
            placeholder="Ask something..."
          />
          <button
            onClick={handleSend}
            className="bg-indigo-500 text-white px-4 py-2 rounded-lg hover:bg-indigo-600"
          >
            Send
          </button>
        </div>
        <button onClick={onBack} className="mt-4 border px-4 py-2 rounded-lg">
          Back
        </button>
      </div>
    </div>
  );
}
