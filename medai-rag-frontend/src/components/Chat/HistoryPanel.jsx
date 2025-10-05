// src/components/Chat/HistoryPanel.jsx
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import * as ChatStore from "../../store/chatStore";

function toDate(v) {
  if (!v) return null;
  if (v.toDate) return v.toDate();
  if (typeof v === "number") return new Date(v);
  if (v.seconds) return new Date(v.seconds * 1000);
  return null;
}
function timeAgo(d) {
  if (!d) return "";
  const s = Math.floor((Date.now() - d.getTime()) / 1000);
  if (s < 60) return "just now";
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  const days = Math.floor(h / 24);
  return `${days}d ago`;
}

export default function HistoryPanel({
  open = true,
  activeId,
  onSelect,
  onNewChat,
  onRename,
  onDelete,
  refreshKey, // parent can bump this to force refresh
}) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editId, setEditId] = useState(null);
  const [editTitle, setEditTitle] = useState("");

  async function refresh() {
    setLoading(true);
    const rows = await ChatStore.listChats();
    setItems(rows);
    setLoading(false);
  }

  useEffect(() => { refresh(); }, []);
  useEffect(() => { if (refreshKey) refresh(); }, [refreshKey]);

  return (
    <aside className={`rounded-2xl border border-gray-200 bg-white p-3 shadow-card ${open ? "" : "hidden lg:block"}`}>
      <div className="mb-2 flex items-center justify-between">
        <div className="text-sm font-semibold">History</div>
        <button
          onClick={onNewChat}
          className="rounded-lg border border-gray-300 px-2 py-1 text-xs hover:bg-gray-50"
          title="Start a new chat"
        >
          + New
        </button>
      </div>

      {loading && (
        <div className="space-y-2">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-8 w-full animate-pulse rounded bg-gray-100" />
          ))}
        </div>
      )}

      {!loading && items.length === 0 && (
        <div className="text-xs text-gray-500">No chats yet.</div>
      )}

      <div className="mt-1 space-y-1">
        {items.map((c, i) => {
          const d = toDate(c.updatedAt);
          const isActive = activeId === c.id;

          return (
            <motion.div
              key={c.id}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.15, delay: i * 0.03 }}
              className={`group rounded-lg px-2 py-2 ${isActive ? "bg-blue-50 border-l-4 border-blue-600" : "border-l-4 border-transparent hover:bg-gray-50"}`}
            >
              {editId === c.id ? (
                <form
                  onSubmit={async (e) => {
                    e.preventDefault();
                    await onRename?.(c.id, editTitle);
                    setEditId(null);
                    setEditTitle("");
                  }}
                  className="flex items-center gap-2"
                >
                  <input
                    autoFocus
                    className="w-full rounded border border-gray-300 px-2 py-1 text-sm"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                  />
                  <button className="rounded bg-blue-600 px-2 py-1 text-white text-xs">Save</button>
                  <button type="button" onClick={()=>{setEditId(null); setEditTitle("")}} className="rounded border px-2 py-1 text-xs">Cancel</button>
                </form>
              ) : (
                <button onClick={() => onSelect?.(c.id)} className="w-full text-left">
                  <div className="flex items-center justify-between">
                    <div className="truncate font-medium text-gray-900 text-sm">{c.title || "Untitled"}</div>
                    <div className="ml-2 shrink-0 text-[10px] text-gray-500">{timeAgo(d)}</div>
                  </div>
                </button>
              )}

              {/* row actions */}
              {editId !== c.id && (
                <div className="mt-1 hidden items-center gap-2 pl-1 text-[11px] text-gray-600 group-hover:flex">
                  <button
                    onClick={() => { setEditId(c.id); setEditTitle(c.title || "Untitled"); }}
                    className="underline-offset-2 hover:underline"
                  >
                    Rename
                  </button>
                  <span className="text-gray-300">•</span>
                  <button
                    onClick={async () => {
                      if (confirm("Delete this chat? This cannot be undone.")) {
                        await onDelete?.(c.id);
                      }
                    }}
                    className="text-red-600 underline-offset-2 hover:underline"
                  >
                    Delete
                  </button>
                </div>
              )}
            </motion.div>
          );
        })}
      </div>
    </aside>
  );
}
