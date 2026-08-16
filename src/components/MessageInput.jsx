import { Paperclip, Send } from "lucide-react";

function MessageInput({
  input,
  setInput,
  handleSend,
}) {

  return (

    <div className="bg-white border-t p-4 flex gap-3">

      <button className="p-2 rounded-lg hover:bg-slate-200">
        <Paperclip />
      </button>

      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            handleSend();
          }
        }}
        className="flex-1 border rounded-xl px-4"
        placeholder="Type your message..."
      />

      <button
        onClick={handleSend}
        className="bg-blue-900 text-white p-3 rounded-xl"
      >
        <Send size={18} />
      </button>

    </div>

  );

}

export default MessageInput;