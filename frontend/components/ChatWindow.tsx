"use client";

import { useEffect, useRef, useState } from "react";
import { sendMessage, ChatResponse } from "@/lib/api";
import MessageBubble from "./MessageBubble";
import ThinkingIndicator from "./ThinkingIndicator";
import QuickStartChips from "./QuickStartChips";
import TicketPanel, { QaEntry } from "./TicketPanel";

interface Message {
  role: "user" | "assistant";
  text: string;
}

const RETRY_PREFIX = "Sorry, I didn't quite catch that. ";

function cleanQuestion(text: string): string {
  return text.startsWith(RETRY_PREFIX) ? text.slice(RETRY_PREFIX.length) : text;
}

function newSessionId(): string {
  return crypto.randomUUID();
}

export default function ChatWindow() {
  const [sessionId, setSessionId] = useState(newSessionId);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [category, setCategory] = useState<string | null>(null);
  const [pendingQuestion, setPendingQuestion] = useState<string | null>(null);
  const [qaLog, setQaLog] = useState<QaEntry[]>([]);
  const [finalResult, setFinalResult] = useState<ChatResponse | null>(null);

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  async function submit(rawText: string) {
    const trimmed = rawText.trim();
    if (!trimmed || loading) return;

    const wasAnswering = pendingQuestion;
    setMessages((prev) => [...prev, { role: "user", text: trimmed }]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const res = await sendMessage(sessionId, trimmed);
      setMessages((prev) => [...prev, { role: "assistant", text: res.reply }]);
      if (res.category) setCategory(res.category);

      const isRetry = res.reply.startsWith(RETRY_PREFIX);
      if (wasAnswering && !isRetry) {
        setQaLog((prev) => [...prev, { question: cleanQuestion(wasAnswering), answer: trimmed }]);
      }

      if (res.is_final) {
        setFinalResult(res);
        setPendingQuestion(null);
      } else {
        setPendingQuestion(cleanQuestion(res.reply));
      }
    } catch {
      setError("Couldn't reach the assistant — check that the backend is running, then try again.");
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setSessionId(newSessionId());
    setMessages([]);
    setInput("");
    setError(null);
    setCategory(null);
    setPendingQuestion(null);
    setQaLog([]);
    setFinalResult(null);
  }

  return (
    <div className="mx-auto grid h-full max-w-5xl grid-cols-1 gap-6 px-4 py-6 lg:grid-cols-[1fr_320px] lg:px-6">
      <div className="flex min-h-0 flex-col">
        <header className="mb-4">
          <h1 className="font-display text-4xl font-semibold leading-none text-ink">
            Smart Product Assistant
          </h1>
          <p className="mt-1.5 text-sm text-inksoft">
            Tell it what you&apos;re building. It asks what it needs to know, then hands you the full list.
          </p>
        </header>

        <div className="flex-1 space-y-3 overflow-y-auto rounded-lg border border-line bg-paper/40 p-4">
          {messages.length === 0 && (
            <div className="space-y-4">
              <p className="text-sm text-inksoft">
                Try one of these, or describe your own project below.
              </p>
              <QuickStartChips onPick={submit} disabled={loading} />
            </div>
          )}
          {messages.map((m, i) => (
            <MessageBubble key={i} role={m.role} text={m.text} />
          ))}
          {loading && <ThinkingIndicator />}
          {error && (
            <div className="rounded-md border border-rust/40 bg-rust-soft px-3.5 py-2.5 text-sm text-rust">
              {error}
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="mt-4 flex gap-2">
          <input
            className="flex-1 rounded-md border border-line bg-surface px-3.5 py-2.5 text-[15px] text-ink placeholder:text-inksoft/70 focus:outline-none focus:ring-2 focus:ring-pine"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && submit(input)}
            placeholder="What are you trying to build or buy?"
            disabled={loading}
          />
          <button
            className="rounded-md bg-pine px-5 py-2.5 text-sm font-medium text-paper transition-colors hover:bg-pine-dark disabled:cursor-not-allowed disabled:opacity-50"
            onClick={() => submit(input)}
            disabled={loading || !input.trim()}
          >
            Send
          </button>
        </div>
      </div>

      <div className="lg:sticky lg:top-6 lg:self-start">
        <TicketPanel
          category={category}
          qaLog={qaLog}
          pendingQuestion={pendingQuestion}
          finalResult={finalResult}
          onReset={handleReset}
        />
      </div>
    </div>
  );
}
