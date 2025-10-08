import { Image, FileText } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import Prism from '../Prism';

export default function ImagePage() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [message, setMessage] = useState("");

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleSubmit = async () => {
    if (!file) return alert("Please select an image or PDF first.");

    setLoading(true);
    setMessage("Uploading your file...");

    try {
      const formData = new FormData();
      formData.append("file", file);
      const token = localStorage.getItem("token");

      const response = await axios.post("http://127.0.0.1:5000/image/upload/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          Authorization: `Bearer ${token}`,
        },
      });

      setLoading(false);
      setMessage("File uploaded successfully!");
      setDone(true);

      navigate("/chat", { state: { 
        fileName: file?.name, 
        fileId: response.data.document_id // updated to match backend
      }});
    } catch (error) {
      setLoading(false);
      setMessage("Error uploading file: " + (error?.response?.data?.detail || error.message));
    }
  };

  const goBack = () => navigate("/home");

  // Determine icon based on file type
  const fileIcon = file?.name?.endsWith(".pdf") ? <FileText className="w-4 h-4 mr-2" /> : <Image className="w-4 h-4 mr-2" />;

  return (
    <div className="relative w-full h-screen overflow-hidden">
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

      <div className="flex items-center justify-center h-screen p-6">
        <div className="bg-black/50 rounded-3xl shadow p-6 w-full max-w-md flex flex-col gap-4">
          <h2 className="font-bold mb-4 text-white text-center text-lg">Upload an Image or PDF</h2>

          {/* File Upload Button */}
          <label className="w-full flex items-center justify-center bg-pink-500 text-white py-2 rounded-lg cursor-pointer hover:bg-pink-600 transition mb-3.5">
            {fileIcon}
            <span>{file ? file.name : "Choose File"}</span>
            <input type="file" accept="image/*,.pdf" className="hidden" onChange={handleFileChange} />
          </label>

          {/* Submit Button */}
          {!done && (
            <button
              onClick={handleSubmit}
              className="w-full flex items-center justify-center bg-green-500 text-white py-2 rounded-lg hover:bg-green-600 transition"
              disabled={loading}
            >
              {loading ? "Uploading..." : "Submit"}
            </button>
          )}

          {/* Status Message */}
          {message && (
            <div className="bg-gray-100 p-3 rounded-lg text-center text-gray-700">
              {message}
            </div>
          )}

          {/* Chat Now Button */}
          {done && (
            <button
              onClick={() => navigate("/chat", { state: { fileName: file?.name } })}
              className="w-full bg-green-500 text-white py-2 rounded-lg hover:bg-green-600 transition"
            >
              Chat Now
            </button>
          )}

          {/* Back Button */}
          <button
            onClick={goBack}
            className="w-full mt-2 text-white border border-pink-500 px-4 py-2 rounded-lg hover:bg-pink-700 transition"
          >
            Back
          </button>
        </div>
      </div>
    </div>
  );
}
