export default function AboutUsPage() {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 p-6 text-center relative">
      <h1 className="text-3xl font-bold mb-4 mt-20">About Us</h1>
      <p className="max-w-2xl text-gray-700 mb-4">
        FileChat was developed by two passionate developers dedicated to making document interaction easier.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl">
        <div className="bg-white shadow rounded-xl p-6">
          <h2 className="font-semibold mb-2">Developer 1</h2>
          <p className="text-gray-600">Specializes in frontend development and user experience design.</p>
        </div>
        <div className="bg-white shadow rounded-xl p-6">
          <h2 className="font-semibold mb-2">Developer 2</h2>
          <p className="text-gray-600">Focuses on backend systems, AI integration, and performance optimization.</p>
        </div>
      </div>
    </div>
  );
}
