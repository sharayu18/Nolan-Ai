import { useEffect, useState } from "react";
import { api, ApiError, type Script, type Topic } from "../lib/api";

const REJECT_REASONS = [
  { value: "too_complex", label: "Too complex" },
  { value: "cannot_demonstrate_at_home", label: "Cannot demonstrate at home" },
  { value: "already_everywhere", label: "Already everywhere" },
  { value: "not_his_style", label: "Not his style" },
  { value: "other", label: "Other" },
];

export default function TopicPicker() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [scripts, setScripts] = useState<Record<string, Script>>({});
  const [searching, setSearching] = useState(false);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      setTopics(await api.listPendingTopics());
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load topics.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const pick = async (topicId: string) => {
    setBusyId(topicId);
    try {
      await api.pickTopic(topicId);
      setTopics((prev) => prev.filter((t) => t.topic_id !== topicId));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not pick topic.");
    } finally {
      setBusyId(null);
    }
  };

  const reject = async (topicId: string, reason: string) => {
    setBusyId(topicId);
    try {
      await api.rejectTopic(topicId, reason);
      setTopics((prev) => prev.filter((t) => t.topic_id !== topicId));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not reject topic.");
    } finally {
      setBusyId(null);
    }
  };

  const runSearch = async () => {
    setSearching(true);
    setError(null);
    try {
      const newTopics = await api.runSearchNow();
      setTopics((prev) => [...newTopics, ...prev]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Search run failed.");
    } finally {
      setSearching(false);
    }
  };

  const generateScript = async (topicId: string) => {
    setBusyId(topicId);
    try {
      const script = await api.generateScript(topicId, "hinglish");
      setScripts((prev) => ({ ...prev, [topicId]: script }));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Script generation failed.");
    } finally {
      setBusyId(null);
    }
  };

  if (loading) return <div className="topic-picker">Loading topics…</div>;

  return (
    <div className="topic-picker">
      <div className="topic-picker-header">
        <h2>Pending topics</h2>
        <div style={{ display: "flex", gap: "8px" }}>
          <button onClick={runSearch} disabled={searching}>
            {searching ? "Running search…" : "Run search now"}
          </button>
          <button onClick={load}>Refresh</button>
        </div>
      </div>
      {searching && (
        <p className="error-text" style={{ color: "var(--muted)" }}>
          Searching this week's category/sub-area and filtering results — this can take up to a minute.
        </p>
      )}
      {error && <p className="error-text">{error}</p>}
      {topics.length === 0 && !searching && (
        <p>No pending topics yet. Click "Run search now" or try "share this week's topics" in chat.</p>
      )}
      {topics.map((topic) => (
        <div key={topic.topic_id} className="topic-card">
          <div className="topic-card-title">{topic.topic_title}</div>
          <div className="topic-card-meta">
            {topic.category} — {topic.sub_area}
          </div>
          <p>{topic.description}</p>
          <div className="topic-card-actions">
            <button disabled={busyId === topic.topic_id} onClick={() => pick(topic.topic_id)}>
              Pick
            </button>
            <select
              disabled={busyId === topic.topic_id}
              defaultValue=""
              onChange={(e) => {
                if (e.target.value) reject(topic.topic_id, e.target.value);
              }}
            >
              <option value="" disabled>
                Reject…
              </option>
              {REJECT_REASONS.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.label}
                </option>
              ))}
            </select>
            <button disabled={busyId === topic.topic_id} onClick={() => generateScript(topic.topic_id)}>
              Generate script
            </button>
          </div>
          {scripts[topic.topic_id] && (
            <div className="script-preview">
              <strong>
                {scripts[topic.topic_id].duration_seconds}s — {scripts[topic.topic_id].complexity}
              </strong>
              <pre>{scripts[topic.topic_id].audio_script}</pre>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
