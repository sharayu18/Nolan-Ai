import { createClient } from "@supabase/supabase-js";

const url = import.meta.env.VITE_SUPABASE_URL as string | undefined;
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;

export const supabaseConfigured = Boolean(url && anonKey);

// Falls back to a placeholder client when unconfigured so the app can still
// render a "set up Supabase" message instead of crashing at import time —
// see Setup Dependencies in docs/HANDOFF.md for creating the project.
export const supabase = createClient(
  url || "https://placeholder.supabase.co",
  anonKey || "placeholder-anon-key",
);
