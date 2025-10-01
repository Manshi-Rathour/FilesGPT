export default function LandingPage() {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-indigo-200 via-purple-200 to-pink-200 p-6 text-center relative">
      <h1 className="text-4xl font-bold mb-4 mt-20">Welcome to FileChat</h1>
      <p className="max-w-xl mb-6 text-gray-700">
        Upload PDFs, images, or websites and start asking questions directly about
        their content. Get instant answers and chat with your documents.
      </p>
    </div>
  );
}
