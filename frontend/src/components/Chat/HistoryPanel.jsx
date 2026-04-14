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

  // NEW: modal state for delete confirm
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [toDelete, setToDelete] = useState(null); // { id, title }

  async function refresh() {
    setLoading(true);
    const rows = await ChatStore.listChats();
    setItems(rows);
    setLoading(false);
  }

  useEffect(() => { refresh(); }, []);
  useEffect(() => { if (refreshKey) refresh(); }, [refreshKey]);

  // NEW: keyboard shortcuts while delete modal is open
  useEffect(() => {
    if (!showDeleteModal) return;
    function onKey(e) {
      if (e.key === "Escape") {
        setShowDeleteModal(false);
        setToDelete(null);
      }
      if (e.key === "Enter") {
        handleConfirmDelete();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showDeleteModal, toDelete]);

  // NEW: confirm/cancel actions
  async function handleConfirmDelete() {
    if (toDelete?.id && onDelete) {
      await onDelete(toDelete.id);
    }
    setShowDeleteModal(false);
    setToDelete(null);
  }
  function handleCancelDelete() {
    setShowDeleteModal(false);
    setToDelete(null);
  }

  return (
    <>
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
                      // OLD: confirm("Delete this chat? ...")
                      // NEW: open our modal instead
                      onClick={() => {
                        setToDelete({ id: c.id, title: c.title || "Untitled" });
                        setShowDeleteModal(true);
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

      {/* NEW: Delete confirm modal (replicates Clear modal styling) */}
      {showDeleteModal && (
        <div
          className="fixed inset-0 z-50 grid place-items-center bg-black/40 backdrop-blur-sm p-4"
          aria-modal="true"
          role="dialog"
        >
          <motion.div
            initial={{ opacity: 0, y: 12, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.98 }}
            className="w-full max-w-md rounded-2xl border border-gray-200 bg-white shadow-2xl"
          >
            <div className="p-5">
              <div className="flex items-start gap-3">
                <div className="h-10 w-10 rounded-full bg-white border border-gray-200 text-gray-900 grid place-items-center shadow-sm">
                  <span aria-hidden>🗑️</span>
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">Delete this chat?</h2>
                  <p className="mt-1 text-sm text-gray-600">
                    <span className="font-medium">{toDelete?.title}</span> will be permanently removed from your history. This cannot be undone.
                  </p>
                </div>
              </div>

              <div className="mt-5 flex items-center justify-end gap-2">
                <button
                  onClick={handleCancelDelete}
                  className="px-4 py-2 rounded-xl border border-gray-300 bg-white text-sm hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmDelete}
                  className="px-4 py-2 rounded-xl bg-gray-900 text-white text-sm hover:bg-gray-800 shadow-sm"
                >
                  Delete now
                </button>
              </div>

              <div className="mt-3 text-[11px] text-gray-500">
                Press <span className="font-semibold">Enter</span> to confirm or <span className="font-semibold">Esc</span> to cancel.
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </>
  );
}
