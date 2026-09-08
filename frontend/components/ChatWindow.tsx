"use client";

import { useState } from "react";
import { sendMessage, ChatResponse } from "@/lib/api";
import MessageBubble from "./MessageBubble";
import ShoppingListCard from "./ShoppingListCard";

interface Message {
  role: "user" | "assistant";
  text: string;
}

export default function ChatWindow() {
  const [sessionId] = useState(() => crypto.randomUUID());
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [finalResult, setFinalResult] = useState<ChatResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSend() {
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const res = await sendMessage(sessionId, trimmed);
      setMessages((prev) => [...prev, { role: "assistant", text: res.reply }]);
      if (res.is_final) setFinalResult(res);
    } catch (err) {
      setError("Something went wrong reaching the assistant. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setMessages([]);
    setFinalResult(null);
    setError(null);
    window.location.reload(); // simplest way to get a fresh session id
  }

  return (
    <div className="flex flex-col h-full max-w-2xl mx-auto p-4">
      <div className="flex-1 overflow-y-auto space-y-2">
        {messages.length === 0 && (
          <p className="text-gray-500 text-sm">
            Tell me what you&apos;re trying to build or buy — e.g. &quot;I want to build a dining table.&quot;
          </p>
        )}
        {messages.map((m, i) => (
          <MessageBubble key={i} role={m.role} text={m.text} />
        ))}
        {loading && <MessageBubble role="assistant" text="Thinking..." />}
        {error && <p className="text-red-600 text-sm">{error}</p>}
        {finalResult?.shopping_list && <ShoppingListCard items={finalResult.shopping_list} />}
      </div>

      <div className="flex gap-2 mt-4">
        <input
          className="flex-1 border rounded px-3 py-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="What are you trying to build or buy?"
          disabled={loading}
        />
        <button
          className="bg-black text-white px-4 py-2 rounded disabled:opacity-50"
          onClick={handleSend}
          disabled={loading}
        >
          Send
        </button>
        {finalResult && (
          <button className="border px-4 py-2 rounded" onClick={handleReset}>
            Start over
          </button>
        )}
      </div>
    </div>
  );
}
