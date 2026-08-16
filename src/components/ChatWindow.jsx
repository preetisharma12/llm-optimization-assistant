import ChatMessage from "./ChatMessage";

function ChatWindow({ messages }) {
  return (
    <div className="flex-1 overflow-y-auto p-8">

      <h2 className="text-2xl font-bold mb-8">
        Conversation
      </h2>

      {messages.map((message, index) => (
        <ChatMessage
          key={index}
          sender={message.sender}
          message={message.text}
        />
      ))}

    </div>
  );
}

export default ChatWindow;