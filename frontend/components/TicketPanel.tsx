"use client";

import { useState } from "react";
import { ChatResponse, humanizeCategory } from "@/lib/api";

export interface QaEntry {
  question: string;
  answer: string;
}

interface TicketPanelProps {
  category: string | null;
  qaLog: QaEntry[];
  pendingQuestion: string | null;
  finalResult: ChatResponse | null;
  onReset: () => void;
}

export default function TicketPanel({
  category,
  qaLog,
  pendingQuestion,
  finalResult,
  onReset,
}: TicketPanelProps) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    if (!finalResult?.shopping_list) return;
    const lines = finalResult.shopping_list.map(
      (item) => `${item.name} — ${item.quantity} ${item.unit}${item.relation_type === "OPTIONAL" ? " (optional)" : ""}`
    );
    try {
      await navigator.clipboard.writeText(lines.join("\n"));
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      // Clipboard permission denied or unavailable — fail silently, list is still on screen.
    }
  }

  const required = finalResult?.shopping_list?.filter((i) => i.relation_type !== "OPTIONAL") ?? [];
  const optional = finalResult?.shopping_list?.filter((i) => i.relation_type === "OPTIONAL") ?? [];

  return (
    <aside className="ticket-perforation rounded-b-lg border border-t-0 border-line bg-surface pt-5 shadow-ticket">
      <div className="px-5 pb-4">
        <p className="font-display text-2xl font-semibold leading-none text-ink">
          {finalResult ? "Your parts list" : "Job ticket"}
        </p>
        <p className="mt-1 text-sm text-inksoft">
          {category ? humanizeCategory(category) : "Waiting on the first detail"}
        </p>
      </div>

      <div className="border-t border-dashed border-line" />

      {!category && (
        <p className="px-5 py-6 text-sm text-inksoft">
          Tell the assistant what you&apos;re building, and this fills in as you go.
        </p>
      )}

      {category && !finalResult && (
        <div className="px-5 py-4">
          <ol className="space-y-3">
            {qaLog.map((entry, i) => (
              <li key={i} className="text-sm">
                <p className="text-inksoft">{entry.question}</p>
                <p className="font-medium text-ink">{entry.answer}</p>
              </li>
            ))}
          </ol>
          {pendingQuestion && (
            <p className="mt-3 text-sm italic text-inksoft">
              Next up — {pendingQuestion}
            </p>
          )}
        </div>
      )}

      {finalResult?.shopping_list && (
        <div className="px-5 py-4">
          <ItemGroup label="Required" items={required} />
          {optional.length > 0 && <ItemGroup label="Optional" items={optional} tone="rust" />}

          <div className="mt-5 flex gap-2 border-t border-dashed border-line pt-4">
            <button
              type="button"
              onClick={handleCopy}
              className="flex-1 rounded-md border border-pine px-3 py-2 text-sm font-medium text-pine transition-colors hover:bg-pine-soft"
            >
              {copied ? "Copied" : "Copy list"}
            </button>
            <button
              type="button"
              onClick={onReset}
              className="flex-1 rounded-md bg-pine px-3 py-2 text-sm font-medium text-paper transition-colors hover:bg-pine-dark"
            >
              Start new job
            </button>
          </div>
        </div>
      )}
    </aside>
  );
}

function ItemGroup({
  label,
  items,
  tone = "pine",
}: {
  label: string;
  items: { name: string; quantity: number; unit: string }[];
  tone?: "pine" | "rust";
}) {
  if (items.length === 0) return null;
  const tagClass = tone === "rust" ? "bg-rust-soft text-rust" : "bg-pine-soft text-pine-dark";
  return (
    <div className="mb-4 last:mb-0">
      <p className={`mb-2 inline-block rounded px-2 py-0.5 text-xs font-medium ${tagClass}`}>{label}</p>
      <ul className="space-y-1.5">
        {items.map((item, i) => (
          <li key={`${item.name}-${i}`} className="flex items-baseline justify-between text-sm">
            <span className="text-ink">{item.name}</span>
            <span className="text-inksoft">
              {item.quantity} {item.unit}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
