import "./index.css";
import { useState } from "react";

import Header from "./components/Header";
import ChatWindow from "./components/ChatWindow";
import MessageInput from "./components/MessageInput";
import InformationPanel from "./components/InformationPanel";

function App() {

  // ==========================
  // Chat Messages
  // ==========================
  const [messages, setMessages] = useState([
    {
      sender: "assistant",
      text: "Hello! What would you like to optimize?",
    },
  ]);

  // ==========================
  // User Input
  // ==========================
  const [input, setInput] =useState("");

  // ==========================
  // Information Panel
  // ==========================
  const [info, setInfo] = useState({
  objective: "",
  parameters: [],
  variables: [],
  constraints: [],
  status: "",
});

  // ==========================
  // Send Message
  // ==========================
  const handleSend = async () => {

  if (input.trim() === "") return;

  // Save input before clearing
  const message = input;

  // Clear the text box immediately
  setInput("");

  // Save user message
  const userMessage = {
    sender: "user",
    text: message,
  };

  setMessages((prev) => [...prev, userMessage]);

  try {

    const response = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: message,
      }),
    });

    const data = await response.json();

    // Assistant reply
    setMessages((prev) => [
      ...prev,
      {
        sender: "assistant",
        text: data.assistant_reply,
      },
    ]);

    // Update Information Panel
    setInfo(data.information);

    // If the interview is finished, automatically build the model
if (data.finished) {

  await fetch("http://127.0.0.1:8000/build_model", {
    method: "POST",
  });

  await fetch("http://127.0.0.1:8000/generate_json", {
    method: "POST",
  });

  setMessages((prev) => [
    ...prev,
    {
      sender: "assistant",
      text: "✅ Optimization model and description generated successfully.",
    },
  ]);
}

  } catch (error) {

    console.error(error);

    setMessages((prev) => [
      ...prev,
      {
        sender: "assistant",
        text: "⚠ Unable to connect to the backend.",
      },
    ]);
  }

};

  return (
    <div className="h-screen flex flex-col bg-slate-100">

      {/* Header */}
      <Header />

      {/* Main Layout */}
      <div className="flex flex-1 overflow-hidden">

        {/* Chat */}
        <div className="flex flex-col flex-1">

          <ChatWindow
            messages={messages}
          />

          <MessageInput
            input={input}
            setInput={setInput}
            handleSend={handleSend}
          />

        </div>

        {/* Right Information Panel */}
        <InformationPanel
          info={info}
        />

      </div>

    </div>
  );
}

export default App;