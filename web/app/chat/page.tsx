"use client";

import React, { useEffect, useMemo, useState } from "react";

type Message = { role: "user" | "assistant"; content: string; ts: number; };
type Chat = { id: string; title: string; messages: Message[]; createdAt: number; updatedAt: number; };

const apiBase =
  (typeof process !== "undefined" && (process as any).env?.NEXT_PUBLIC_API_BASE) ||
  (typeof window !== "undefined" && (window as any).__NEXT_PUBLIC_API_BASE) ||
  "https://app.scriptonika.ru";

function uuid() { return Math.random().toString(36).slice(2) + Date.now().toString(36); }
function loadChats(): Chat[] { try { const raw = localStorage.getItem("skriptonika_chats"); return raw ? JSON.parse(raw) : []; } catch { return []; } }
function saveChats(chats: Chat[]) { localStorage.setItem("skriptonika_chats", JSON.stringify(chats)); }

export default function ChatPage() {
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeId, setActiveId] = useState<string>("");
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const activeChat = useMemo(() => chats.find((c) => c.id === activeId) || null, [chats, activeId]);

  useEffect(() => { const initial = loadChats(); setChats(initial); if (initial.length) setActiveId(initial[0].id); }, []);
  useEffect(() => { saveChats(chats); }, [chats]);

  function createChat() {
    const id = uuid(), now = Date.now();
    const chat: Chat = { id, title: "Новый диалог", messages: [], createdAt: now, updatedAt: now };
    setChats((prev) => [chat, ...prev]); setActiveId(id);
  }
  function deleteChat(id: string) {
    setChats((prev) => prev.filter((c) => c.id !== id));
    if (activeId === id) { const rest = chats.filter((c) => c.id !== id); setActiveId(rest[0]?.id || ""); }
  }
  function renameChat(id: string) {
    const title = prompt("Новое название чата:"); if (!title) return;
    setChats((prev) => prev.map((c) => (c.id === id ? { ...c, title, updatedAt: Date.now() } : c)));
  }

  async function send() {
    const question = input.trim(); if (!question || !activeChat || loading) return;
    setLoading(true); setInput("");
    setChats((prev) => prev.map((c) => c.id === activeChat.id ? {
      ...c, messages: [...c.messages, { role: "user", content: question, ts: Date.now() }],
      title: c.messages.length === 0 && question.length > 3 ? question.slice(0, 40) : c.title, updatedAt: Date.now()
    } : c));

    try {
      const resp = await fetch(`${apiBase}/api/ask`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, top_k: 3 })
      });
      if (!resp.ok) throw new Error(await resp.text());
      const data = await resp.json();
      const answer = data?.answer || "Ответ не получен. Проверьте публикацию и реиндексацию БЗ.";
      setChats((prev) => prev.map((c) => c.id === activeChat.id ? {
        ...c, messages: [...c.messages, { role: "assistant", content: answer, ts: Date.now() }], updatedAt: Date.now()
      } : c));
    } catch (e:any) {
      setChats((prev) => prev.map((c) => c.id === activeChat.id ? {
        ...c, messages: [...c.messages, { role: "assistant", content: "Ошибка API: "+(e?.message||e), ts: Date.now() }], updatedAt: Date.now()
      } : c));
    } finally { setLoading(false); }
  }

  useEffect(() => {
    function onKeydown(e: KeyboardEvent) { if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); send(); } }
    window.addEventListener("keydown", onKeydown);
    return () => window.removeEventListener("keydown", onKeydown);
  }, [send]);

  return (
    <div style={{ display: "flex", height: "100vh", fontFamily: "system-ui, sans-serif" }}>
      <aside style={{ width: 280, borderRight: "1px solid #e5e7eb", display: "flex", flexDirection: "column" }}>
        <div style={{ padding: 12, borderBottom: "1px solid #e5e7eb" }}>
          <button onClick={createChat} style={{ width: "100%", padding: "10px 12px", border: "1px solid #d1d5db", background: "#fff", cursor: "pointer", borderRadius: 8, fontWeight: 600 }}>
            + Новый диалог
          </button>
        </div>
        <div style={{ overflowY: "auto" }}>
          {chats.length === 0 ? (
            <div style={{ padding: 12, color: "#6b7280" }}>Диалогов пока нет</div>
          ) : (
            chats.map((c) => (
              <div key={c.id} onClick={() => setActiveId(c.id)} style={{ padding: 12, borderBottom: "1px solid #f3f4f6", background: c.id === activeId ? "#f3f4f6" : "transparent", cursor: "pointer" }}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}>
                  <div style={{ fontWeight: 600, flex: 1, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{c.title || "Без названия"}</div>
                  <div style={{ display: "flex", gap: 6 }}>
                    <button onClick={(e) => { e.stopPropagation(); renameChat(c.id); }} title="Переименовать" style={{ border: "none", background: "transparent", cursor: "pointer" }}>✏️</button>
                    <button onClick={(e) => { e.stopPropagation(); if (confirm("Удалить диалог?")) deleteChat(c.id); }} title="Удалить" style={{ border: "none", background: "transparent", cursor: "pointer" }}>🗑️</button>
                  </div>
                </div>
                <div style={{ color: "#6b7280", fontSize: 12, marginTop: 4 }}>{new Date(c.updatedAt).toLocaleString()}</div>
              </div>
            ))
          )}
        </div>
      </aside>

      <main style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        <div style={{ padding: 12, borderBottom: "1px solid #e5e7eb", fontWeight: 700 }}>Skriptonika — чат</div>
        <div style={{ flex: 1, overflowY: "auto", padding: 16 }}>
          {!activeChat || activeChat.messages.length === 0 ? (
            <div style={{ color: "#6b7280" }}>
              Напишите вопрос справа внизу. <br />
              Подсказка: опубликуйте записи в базе знаний и нажмите «Переиндексировать» — ответы станут богаче.
            </div>
          ) : (
            activeChat.messages.map((m, i) => (
              <div key={i} style={{ margin: "8px 0", display: "flex", justifyContent: m.role === "user" ? "flex-end" : "flex-start" }}>
                <div style={{ maxWidth: 760, padding: "10px 12px", borderRadius: 10, background: m.role === "user" ? "#e0f2fe" : "#f3f4f6", whiteSpace: "pre-wrap" }}>
                  <div style={{ fontSize: 12, color: "#6b7280", marginBottom: 4 }}>{m.role === "user" ? "Вы" : "Скриптоника"}</div>
                  <div>{m.content}</div>
                </div>
              </div>
            ))
          )}
        </div>
        <div style={{ padding: 12, borderTop: "1px solid #e5e7eb" }}>
          {activeId ? (
            <div style={{ display: "flex", gap: 8 }}>
              <textarea rows={2} placeholder="Введите вопрос (Ctrl/⌘+Enter — отправить)" value={input} onChange={(e) => setInput(e.target.value)}
                style={{ flex: 1, padding: 10, border: "1px solid #d1d5db", borderRadius: 8, resize: "vertical" }} disabled={loading} />
              <button onClick={send} disabled={loading || !input.trim()}
                style={{ padding: "0 16px", border: "1px solid #2563eb", background: loading ? "#93c5fd" : "#3b82f6", color: "#fff", borderRadius: 8, cursor: loading ? "default" : "pointer", fontWeight: 600 }}>
                {loading ? "Ждём..." : "Спросить"}
              </button>
            </div>
          ) : (
            <button onClick={createChat} style={{ padding: "10px 12px", border: "1px solid #d1d5db", background: "#fff", cursor: "pointer", borderRadius: 8, fontWeight: 600 }}>
              Создать первый диалог
            </button>
          )}
        </div>
      </main>
    </div>
  );
}
