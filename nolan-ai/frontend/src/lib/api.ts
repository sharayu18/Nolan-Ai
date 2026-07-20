import { supabase } from "./supabaseClient";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string) || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function authHeader(): Promise<Record<string, string>> {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = {
    "Content-Type": "application/json",
    ...(await authHeader()),
    ...(options.headers || {}),
  };
  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new ApiError(response.status, body.detail || response.statusText);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

export type Topic = {
  topic_id: string;
  topic_title: string;
  category: string;
  sub_area: string;
  description: string;
  pillar: string | null;
  source: string;
  status: string;
  reason: string | null;
  created_at: string;
};

export type ChatResponse = {
  intent: string;
  reply: string;
  data?: unknown;
};

export type Script = {
  script_id: string;
  topic_id: string;
  topic_title: string;
  language: string;
  complexity: string;
  duration_seconds: number;
  audio_script: string;
  video_script: string;
  hook_1: string;
  hook_2: string;
  hook_3: string;
  caption_1: string;
  caption_2: string;
  caption_3: string;
  hashtags: string;
  text_overlay_start: string;
  text_overlay_mid: string;
  audio_suggestion: string;
};

export const api = {
  chat: (message: string, extra: Record<string, unknown> = {}) =>
    request<ChatResponse>("/chat", {
      method: "POST",
      body: JSON.stringify({ message, ...extra }),
    }),

  listPendingTopics: () => request<Topic[]>("/topics?status=pending_to_pick"),

  pickTopic: (topicId: string) =>
    request<Topic>(`/topics/${topicId}/pick`, { method: "POST" }),

  rejectTopic: (topicId: string, reason: string) =>
    request<Topic>(`/topics/${topicId}/reject`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    }),

  generateScript: (topicId: string, language: "hinglish" | "english") =>
    request<Script>("/scripts/generate", {
      method: "POST",
      body: JSON.stringify({ topic_id: topicId, language }),
    }),
};
