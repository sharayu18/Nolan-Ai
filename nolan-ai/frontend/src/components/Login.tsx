import { supabaseConfigured } from "../lib/supabaseClient";

type Props = {
  onSignIn: () => void;
};

export default function Login({ onSignIn }: Props) {
  return (
    <div className="login-screen">
      <h1>Nolan AI</h1>
      <p className="subtitle">@physicsexperimental — content pipeline</p>
      {supabaseConfigured ? (
        <button className="google-btn" onClick={onSignIn}>
          Sign in with Google
        </button>
      ) : (
        <p className="config-warning">
          Supabase isn't configured yet — set <code>VITE_SUPABASE_URL</code> and{" "}
          <code>VITE_SUPABASE_ANON_KEY</code> in <code>.env</code> once the Supabase
          project exists (see Setup Dependencies in <code>docs/HANDOFF.md</code>).
        </p>
      )}
    </div>
  );
}
