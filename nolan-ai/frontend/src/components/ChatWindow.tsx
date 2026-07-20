import { useState } from "react";
import { api, ApiError } from "../lib/api";

type Message = {
  role: "user" | "agent";
  text: string;
};

const SUGGESTIONS = [
  "Share this week's topics",
  "How is my channel doing?",
];

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "agent",
      text: "Hi — try \"share this week's topics\" or \"how is my channel doing\". Pick/reject topics and script generation happen from the Topics panel.",
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);

  const send = async (text: string) => {
    const message = text.trim();
    if (!message || sending) return;
    setMessages((prev) => [...prev, { role: "user", text: message }]);
    setInput("");
    setSending(true);
    try {
      const response = await api.chat(message);
      setMessages((prev) => [...prev, { role: "agent", text: response.reply }]);
    } catch (err) {
      const text = err instanceof ApiError ? err.message : "Something went wrong reaching the backend.";
      setMessages((prev) => [...prev, { role: "agent", text }]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="chat-window">
      <div className="chat-messages">
        {messages.map((m, i) => (
          <div key={i} className={`chat-bubble ${m.role}`}>
            <pre>{m.text}</pre>
          </div>
        ))}
        {sending && <div className="chat-bubble agent typing">…</div>}
      </div>
      <div className="chat-suggestions">
        {SUGGESTIONS.map((s) => (
          <button key={s} onClick={() => send(s)} disabled={sending}>
            {s}
          </button>
        ))}
      </div>
      <form
        className="chat-input-row"
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Message Nolan AI…"
          disabled={sending}
        />
        <button type="submit" disabled={sending || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
