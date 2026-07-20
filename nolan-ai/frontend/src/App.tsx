import { useState } from "react";
import "./App.css";
import Login from "./components/Login";
import ChatWindow from "./components/ChatWindow";
import TopicPicker from "./components/TopicPicker";
import { useAuth } from "./lib/useAuth";
import { supabaseConfigured } from "./lib/supabaseClient";

type Tab = "chat" | "topics";

function App() {
  const { session, loading, signInWithGoogle, signOut } = useAuth();
  const [tab, setTab] = useState<Tab>("chat");

  if (loading) return <div className="center-screen">Loading…</div>;

  // Without a configured Supabase project there's no session to gate on —
  // fall through so the app is still usable locally against the backend.
  if (supabaseConfigured && !session) {
    return <Login onSignIn={signInWithGoogle} />;
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>Nolan AI</h1>
        <nav className="tabs">
          <button className={tab === "chat" ? "active" : ""} onClick={() => setTab("chat")}>
            Chat
          </button>
          <button className={tab === "topics" ? "active" : ""} onClick={() => setTab("topics")}>
            Topics
          </button>
        </nav>
        {session && (
          <div className="user-info">
            <span>{session.user.email}</span>
            <button onClick={signOut}>Sign out</button>
          </div>
        )}
      </header>
      <main className="app-main">
        {tab === "chat" ? <ChatWindow /> : <TopicPicker />}
      </main>
    </div>
  );
}

export default App;
