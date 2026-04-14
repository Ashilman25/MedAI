// src/store/chatStore.js
import { nanoid } from "nanoid";
import {
  addMessage,
  createChatDoc,
  listUserChats,
  loadMessages,
  renameChatDoc,
  deleteChatCascade,
} from "../lib/db";

// ---- Guest (localStorage) helpers
const GKEY = "medai_guest_chats_v1";
const MAX_GUEST_CHATS = 3;
const MAX_GUEST_MSGS = 30;

function readLocal() {
  try { return JSON.parse(localStorage.getItem(GKEY)) ?? {}; } catch { return {}; }
}
function writeLocal(data) {
  localStorage.setItem(GKEY, JSON.stringify(data));
}

let MODE = "guest"; // 'guest' | 'user'
let UID = null;

export function initSession({ user }) {
  MODE = user ? "user" : "guest";
  UID = user?.uid ?? null;
}

export function hasGuestDraft() {
  const data = readLocal();
  return Object.keys(data).length > 0;
}

export async function migrateGuestChatToUser() {
  if (MODE !== "user" || !UID) return;
  const data = readLocal();
  const ids = Object.keys(data);
  if (ids.length === 0) return;
  const first = data[ids[0]];
  const firstUserMsg = (first?.messages || []).find(m => m.role === "user")?.content || "Imported chat";
  const chatId = await createChatDoc(UID, firstUserMsg);
  for (const m of first.messages) {
    await addMessage(UID, chatId, m);
  }
  localStorage.removeItem(GKEY);
  return chatId;
}

// ---- Public API
export async function createChat(initialMessageText = "") {
  if (MODE === "guest") {
    const data = readLocal();
    let keys = Object.keys(data);
    // trim to max chats
    if (keys.length >= MAX_GUEST_CHATS) {
      const drop = keys[keys.length - 1];
      delete data[drop];
    }
    const chatId = nanoid();
    data[chatId] = { id: chatId, updatedAt: Date.now(), title: (initialMessageText || "New chat").slice(0,80), messages: [] };
    writeLocal(data);
    return { chatId };
  } else {
    const chatId = await createChatDoc(UID, initialMessageText);
    return { chatId };
  }
}

export async function appendMessage(chatId, message) {
  if (MODE === "guest") {
    const data = readLocal();
    if (!data[chatId]) data[chatId] = { id: chatId, updatedAt: Date.now(), title: "New chat", messages: [] };
    const msgs = data[chatId].messages;
    // trim per-chat size
    if (msgs.length >= MAX_GUEST_MSGS) msgs.shift();
    msgs.push({
      role: message.role,
      content: message.content,
      citations: message.citations || [],
      confidence: message.confidence ?? null,
      createdAt: message.createdAt ?? Date.now(),
    });
    if (!data[chatId].title && message.role === "user") {
      data[chatId].title = (message.content || "").slice(0,80);
    }
    data[chatId].updatedAt = Date.now();
    writeLocal(data);
  } else {
    await addMessage(UID, chatId, message);
  }
}

export async function listChats() {
  if (MODE === "guest") {
    const data = readLocal();
    return Object.values(data)
      .sort((a,b) => (b.updatedAt||0)-(a.updatedAt||0))
      .map(c => ({ id: c.id, title: c.title, updatedAt: c.updatedAt }));
  } else {
    return await listUserChats(UID);
  }
}

export async function loadChat(chatId) {
  if (!chatId) return [];
  if (MODE === "guest") {
    const data = readLocal();
    return data[chatId]?.messages ?? [];
  } else {
    return await loadMessages(UID, chatId);
  }
}

export async function renameChat(chatId, title) {
  if (MODE === "guest") {
    const data = readLocal();
    if (data[chatId]) { data[chatId].title = (title || "Untitled").slice(0,80); writeLocal(data); }
  } else {
    await renameChatDoc(UID, chatId, title);
  }
}

export async function deleteChat(chatId) {
  if (MODE === "guest") {
    const data = readLocal();
    delete data[chatId];
    writeLocal(data);
  } else {
    await deleteChatCascade(UID, chatId);
  }
}
