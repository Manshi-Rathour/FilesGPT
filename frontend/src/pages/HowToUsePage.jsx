export default function HowToUsePage() {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-indigo-100 via-purple-100 to-pink-100 p-6 text-center relative">
      <h1 className="text-3xl font-bold mb-4 mt-20">How to Use FileChat</h1>
      <ul className="max-w-2xl text-left space-y-4 text-gray-700">
        <li>1. Login or Signup to access the platform.</li>
        <li>2. Select whether you want to upload a PDF, Image, or Website link.</li>
        <li>3. Provide your file or link input.</li>
        <li>4. Start chatting with your material and ask questions!</li>
      </ul>
    </div>
  );
}
