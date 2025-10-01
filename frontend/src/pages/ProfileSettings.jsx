import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function ProfileSettings() {
  const navigate = useNavigate();

  // Example user state (replace with data from your backend or context)
  const [profile, setProfile] = useState({
    name: "John Doe",
    email: "john@example.com",
    avatar: "",
    password: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProfile((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: send updated profile to backend
    console.log("Profile updated:", profile);
    alert("Profile saved successfully!");
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-gradient-to-br from-indigo-200 via-purple-200 to-pink-200">
      <div className="bg-white shadow-lg rounded-2xl p-8 w-full max-w-md">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6 text-center">
          Profile Settings
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Avatar */}
          <div className="flex flex-col items-center">
            {profile.avatar ? (
              <img
                src={profile.avatar}
                alt="Avatar"
                className="w-20 h-20 rounded-full mb-2"
              />
            ) : (
              <div className="w-20 h-20 rounded-full bg-gray-300 flex items-center justify-center text-gray-600 text-xl mb-2">
                {profile.name.charAt(0).toUpperCase()}
              </div>
            )}
            <input
              type="text"
              name="avatar"
              value={profile.avatar}
              onChange={handleChange}
              placeholder="Avatar URL"
              className="w-full px-3 py-2 border rounded-lg text-sm"
            />
          </div>

          {/* Name */}
          <div>
            <label className="block text-gray-600 text-sm mb-1">Name</label>
            <input
              type="text"
              name="name"
              value={profile.name}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded-lg"
            />
          </div>

          {/* Email */}
          <div>
            <label className="block text-gray-600 text-sm mb-1">Email</label>
            <input
              type="email"
              name="email"
              value={profile.email}
              disabled
              className="w-full px-3 py-2 border rounded-lg bg-gray-100 text-gray-500 cursor-not-allowed"
            />
          </div>

          {/* Password */}
          <div>
            <label className="block text-gray-600 text-sm mb-1">New Password</label>
            <input
              type="password"
              name="password"
              value={profile.password}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Enter new password"
            />
          </div>

          {/* Buttons */}
          <div className="flex justify-between mt-6">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
            >
              Back
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
