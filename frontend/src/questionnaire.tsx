import React, { useState, useEffect } from "react";
import { Send, ArrowRight, CheckCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";

const QUESTIONS = [
  "Tell me a little about yourself! How would you describe yourself in a few words?",
  "Tell me about your Friends and Family..",
  "What are some things you enjoy doing in your free time?",
  "How are you feeling today—emotionally and psychologically?",
  "What’s making you feel this way?",
  "If you could change one thing about your current situation to feel better, what would it be?"
];

interface QuestionnaireProps {
  userInfo: { name: string; age: string; gender: string };
}

const Questionnaire: React.FC<QuestionnaireProps> = ({ userInfo }) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [responses, setResponses] = useState<Record<string, string>>({});
  const [answer, setAnswer] = useState("");
  const [isComplete, setIsComplete] = useState(false);
  const [animation, setAnimation] = useState(false);  // ✅ Fixed missing state
  const [loading, setLoading] = useState(false);
  const [generatedStory, setGeneratedStory] = useState<string | null>(null); // ✅ Fixed missing state
  const navigate = useNavigate();

  // Function to send answer to FastAPI
  const processAnswer = async (text: string) => {
    setLoading(true);
    const storedUserInfo = JSON.parse(localStorage.getItem("userInfo") || "null");
  
    if (!storedUserInfo) {
      console.error("❌ User info missing!"); // ✅ Debugging
      alert("User info is missing! Please start again.");
      navigate("/");
      return;
    }
  
    console.log("📤 Sending Data:", { text, user_info: storedUserInfo });
  
    try {
      const response = await fetch("http://127.0.0.1:8000/process-answer/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, user_info: storedUserInfo }),
      });
  
      if (!response.ok) throw new Error("Failed to process answer.");
      console.log("✅ Answer stored:", await response.json());
    } catch (error) {
      console.error("❌ Error:", error);
    }
    setLoading(false);
  };
  
  

  // Handle form submission
  const submitAnswer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!answer.trim()) return;

    setResponses((prev) => ({ ...prev, [QUESTIONS[currentQuestionIndex]]: answer }));
    await processAnswer(answer);

    // Animate transition
    setAnimation(true);
    setTimeout(() => {
      setAnswer("");
      if (currentQuestionIndex >= QUESTIONS.length - 1) {
        setIsComplete(true);
      } else {
        setCurrentQuestionIndex((prev) => prev + 1);
      }
      setAnimation(false);
    }, 400);
  };

  // Fetch the story once all questions are answered
  useEffect(() => {
    if (isComplete) {
      fetchStory();
    }
  }, [isComplete]);

  const fetchStory = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/generate-story/");
      if (!response.ok) {
        throw new Error("Failed to generate story.");
      }
      const data = await response.json();
      console.log("📖 Generated Story:", data.story);
      setGeneratedStory(data.story);
    } catch (error) {
      console.error("❌ Error fetching story:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-50 to-blue-100 flex items-center justify-center p-4">
      <div className="w-full max-w-lg h-[650px] bg-white rounded-2xl shadow-xl overflow-hidden">
        {/* Header */}
        <div className="bg-indigo-600 p-6 text-white">
          <h1 className="text-2xl font-bold">Interactive Questionnaire</h1>
          <p className="text-indigo-100 mt-1">Share your thoughts with us</p>
        </div>

        {/* Content */}
        <div className="p-6">
          {!isComplete ? (
            <form onSubmit={submitAnswer} className={`transition-opacity duration-300 ${animation ? "opacity-0" : "opacity-100"}`}>
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                {QUESTIONS[currentQuestionIndex]}
              </h2>
              <div className="relative">
                <textarea
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  className="w-full p-4 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition resize-none overflow-y-auto"
                  placeholder="Your answer here..."
                />
                <button
                  type="submit"
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-indigo-600 text-white p-2 rounded-full hover:bg-indigo-700 transition-colors disabled:opacity-50"
                  disabled={!answer.trim() || loading}
                >
                  {loading ? "..." : currentQuestionIndex < QUESTIONS.length - 1 ? <ArrowRight size={20} /> : <Send size={20} />}
                </button>
              </div>
            </form>
          ) : (
            <div className="text-center py-8 space-y-6 animate-fade-in">
              <div className="flex justify-center">
                <div className="bg-green-100 p-4 rounded-full">
                  <CheckCircle size={48} className="text-green-600" />
                </div>
              </div>
              <h2 className="text-2xl font-bold text-gray-800">Your Personalized Story</h2>
              {generatedStory ? (
                <p className="text-gray-700 text-lg leading-relaxed px-4">{generatedStory}</p>
              ) : (
                <p className="text-gray-600">Generating your story... Please wait.</p>
              )}

              <button
                onClick={() => {
                  setCurrentQuestionIndex(0);
                  setResponses({});
                  setIsComplete(false);
                  setGeneratedStory(null);
                  navigate("/"); // Navigate back to user info form
                }}
                className="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Start Over
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Questionnaire;
