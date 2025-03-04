import React, { useState } from "react";
import { BrowserRouter as Router, Route, Routes, useNavigate } from "react-router-dom";
import UserInfo from "./userInfo";
import Questionnaire from "./questionnaire";

function App() {
  const [userInfo, setUserInfo] = useState<{ name: string; age: string; gender: string } | null>(
    () => JSON.parse(localStorage.getItem("userInfo") || "null")
  );
  
  const handleUserSubmit = (info: { name: string; age: string; gender: string }) => {
    setUserInfo(info);
    localStorage.setItem("userInfo", JSON.stringify(info)); // ✅ Save in localStorage
  };
  

  return (
    <Router>
      <Routes>
        {/* Route for user info form */}
        <Route path="/" element={<UserInfo onSubmit={setUserInfo} />} />
        
        {/* Route for questionnaire (only accessible after user submits info) */}
        <Route 
          path="/questionnaire" 
          element={userInfo ? <Questionnaire userInfo={userInfo} /> : <RedirectToHome />} 
        />
      </Routes>
    </Router>
  );
}

// ✅ Redirects to home if user info is not set (prevents manual navigation to /questionnaire)
const RedirectToHome = () => {
  const navigate = useNavigate();
  React.useEffect(() => {
    navigate("/");
  }, []);
  return null;
};

export default App;
