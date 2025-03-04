import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { User, Users } from "lucide-react";

interface UserInfoProps {
  onSubmit: (userInfo: { name: string; age: string; gender: string }) => void;
}

const UserInfo: React.FC<UserInfoProps> = ({ onSubmit }) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ name: "", age: "", gender: "" });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.age || !formData.gender) {
      alert("Please fill all fields!");
      return;
    }
  
    try {
      console.log("📤 Sending user info:", formData);
      const response = await fetch("http://127.0.0.1:8000/store-user/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
  
      if (!response.ok) {
        throw new Error(`❌ Request failed: ${response.status} ${response.statusText}`);
      }
  
      console.log("✅ User info stored in FastAPI");
  
      localStorage.setItem("userInfo", JSON.stringify(formData)); // ✅ Save in localStorage
      onSubmit(formData); // ✅ Update state
      navigate("/questionnaire");
    } catch (error) {
      console.error("❌ Error storing user info:", error);
      if (error instanceof Error) {
        alert(`Error storing user info: ${error.message}`);
      } else {
        alert('An unknown error occurred.');
      }
    }
  };
  
  

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-lg shadow-md overflow-hidden">
        <div className="bg-blue-600 p-4 flex items-center justify-center">
          <Users className="text-white mr-2" size={24} />
          <h1 className="text-xl font-bold text-white">User Information</h1>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Name Input */}
          <div className="space-y-2">
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">Full Name</label>
            <input type="text" id="name" name="name" value={formData.name} onChange={handleChange} required className="block w-full rounded-md border-gray-300 p-2" placeholder="Enter your name" />
          </div>

          {/* Gender Selection */}
          <div className="space-y-2">
            <label htmlFor="gender" className="block text-sm font-medium text-gray-700">Gender</label>
            <select id="gender" name="gender" value={formData.gender} onChange={handleChange} required className="block w-full rounded-md border-gray-300 p-2">
              <option value="">Select gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>

          {/* Age Input */}
          <div className="space-y-2">
            <label htmlFor="age" className="block text-sm font-medium text-gray-700">Age</label>
            <input type="number" id="age" name="age" value={formData.age} onChange={handleChange} required className="block w-full rounded-md border-gray-300 p-2" placeholder="Enter your age" />
          </div>

          {/* Submit Button */}
          <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded-md">Start</button>
        </form>
      </div>
    </div>
  );
};

export default UserInfo;
