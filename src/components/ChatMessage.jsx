function ChatMessage({ sender, message }) {
  const isUser = sender === "user";

  return (
    <div className="mb-8">

      <p
        className={`text-sm font-semibold mb-2 ${
          isUser ? "text-blue-700" : "text-gray-700"
        }`}
      >
        {isUser ? "You" : "Assistant"}
      </p>

      <div
        className={`rounded-2xl px-5 py-4 max-w-2xl shadow-sm ${
          isUser
            ? "bg-blue-900 text-white ml-auto"
            : "bg-white text-gray-800"
        }`}
      >
        {message}
      </div>

    </div>
  );
}

export default ChatMessage;