import { FileText } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

export default function PDFPage() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [message, setMessage] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async () => {
    if (!file) {
      alert("Please select a PDF first.");
      return;
    }

    setLoading(true);
    setMessage("Model is training on your PDF...");

    try {
      const formData = new FormData();
      formData.append("file", file);
      const token = localStorage.getItem("token");

      const response = await axios.post("http://127.0.0.1:5000/pdf/upload/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          Authorization: `Bearer ${token}`,
        },
      });

      setLoading(false);
      setMessage(`PDF processed successfully! Chunks: ${response.data.chunks}`);
      setDone(true);
      
      navigate("/chat", {
        state: {
          pdfName: file?.name,
          documentId: response.data.document_id
        }
      });

    } catch (error) {
      setLoading(false);
      setMessage("Error processing PDF: " + (error?.response?.data?.detail || error.message));
    }
  };


  const goHome = () => navigate("/home");
  const goChat = () => navigate("/chat", { state: { pdfName: file?.name } });

  return (
    <div className="flex items-center justify-center h-screen bg-gradient-to-br from-indigo-200 via-purple-200 to-pink-200 p-6 pt-[80px]">
      <div className="bg-white rounded-xl shadow p-6 w-full max-w-md flex flex-col gap-4">
        <h2 className="font-bold mb-4 text-center text-lg">Upload a PDF</h2>

        {/* Custom file input */}
        <label className="w-full flex items-center justify-center bg-indigo-500 text-white py-2 rounded-lg cursor-pointer hover:bg-indigo-600 transition">
          <FileText className="w-4 h-4 mr-2 text-white" />
          <span className="text-white">
            {file ? file.name : "Choose PDF"}
          </span>
          <input type="file" accept="application/pdf" className="hidden" onChange={handleFileChange} />
        </label>

        {!done && (
          <button
            onClick={handleSubmit}
            className="w-full flex items-center justify-center bg-green-500 text-white py-2 rounded-lg hover:bg-green-600 transition mt-2"
            disabled={loading}
          >
            {loading ? "Processing..." : "Submit"}
          </button>
        )}

        {message && (
          <div className="bg-gray-100 p-3 rounded-lg text-center text-gray-700">
            {message}
          </div>
        )}

        {done && (
          <button
            onClick={goChat}
            className="w-full bg-green-500 text-white py-2 rounded-lg hover:bg-green-600 transition mt-2"
          >
            Chat Now
          </button>
        )}

        <button
          onClick={goHome}
          className="w-full border border-gray-300 py-2 rounded-lg hover:bg-gray-100 transition mt-2"
        >
          Go to Home Page
        </button>
      </div>
    </div>
  );
}
