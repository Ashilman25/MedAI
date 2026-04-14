// src/lib/db.js
import {
  getFirestore,
  collection,
  addDoc,
  setDoc,
  doc,
  getDocs,
  query,
  orderBy,
  serverTimestamp,
  deleteDoc,
} from "firebase/firestore";
import { app } from "./firebase";

export const db = getFirestore(app);

export async function createChatDoc(uid, firstText) {
  const ref = await addDoc(collection(db, "users", uid, "chats"), {
    title: (firstText || "New chat").slice(0, 80),
    createdAt: serverTimestamp(),
    updatedAt: serverTimestamp(),
    lastSummary: "",
    lastConfidence: 0,
  });
  return ref.id;
}

export async function addMessage(uid, chatId, msg) {
  const mref = collection(db, "users", uid, "chats", chatId, "messages");
  await addDoc(mref, {
    role: msg.role,
    content: msg.content,
    citations: msg.citations || [],
    confidence: msg.confidence ?? null,
    createdAt: serverTimestamp(),
  });
  // keep chat "fresh" in lists
  await setDoc(
    doc(db, "users", uid, "chats", chatId),
    {
      title: msg.role === "user" ? (msg.content || "").slice(0, 80) : undefined,
      lastConfidence: msg.confidence ?? undefined,
      updatedAt: serverTimestamp(),
    },
    { merge: true }
  );
}

export async function listUserChats(uid) {
  const ref = collection(db, "users", uid, "chats");
  const snap = await getDocs(query(ref, orderBy("updatedAt", "desc")));
  return snap.docs.map((d) => ({ id: d.id, ...d.data() }));
}

export async function loadMessages(uid, chatId) {
  const ref = collection(db, "users", uid, "chats", chatId, "messages");
  const snap = await getDocs(query(ref, orderBy("createdAt", "asc")));
  return snap.docs.map((d) => ({ id: d.id, ...d.data() }));
}

// --- NEW: rename + cascade delete ---
export async function renameChatDoc(uid, chatId, title) {
  const cref = doc(db, "users", uid, "chats", chatId);
  await setDoc(
    cref,
    { title: (title || "Untitled").slice(0, 80), updatedAt: serverTimestamp() },
    { merge: true }
  );
}

export async function deleteChatCascade(uid, chatId) {
  // delete all messages
  const mref = collection(db, "users", uid, "chats", chatId, "messages");
  const msnap = await getDocs(mref);
  const deletes = msnap.docs.map((d) => deleteDoc(d.ref));
  await Promise.all(deletes);
  // delete chat
  await deleteDoc(doc(db, "users", uid, "chats", chatId));
}

/**
 * Source Sets (nice-to-have)
 */
export async function saveSourceSet(uid, payload) {
  // payload: { name, keywords, options, createdAt }
  const ref = collection(db, "users", uid, "source_sets");
  await addDoc(ref, payload);
}

export async function listSourceSets(uid) {
  const ref = collection(db, "users", uid, "source_sets");
  const snap = await getDocs(query(ref, orderBy("createdAt", "desc")));
  return snap.docs.map((d) => ({ id: d.id, ...d.data() }));
}
