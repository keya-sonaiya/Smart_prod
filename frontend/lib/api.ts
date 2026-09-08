const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export interface ShoppingListItem {
  name: string;
  quantity: number;
  unit: string;
  relation_type: string;
}

export interface ChatResponse {
  session_id: string;
  reply: string;
  is_final: boolean;
  shopping_list?: ShoppingListItem[];
  category?: string;
}

export async function sendMessage(sessionId: string, message: string): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message }),
  });
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  return res.json();
}

/** Turns a category key like "dining_table" into "Dining table" for display. */
export function humanizeCategory(key: string): string {
  const words = key.split("_").join(" ");
  return words.charAt(0).toUpperCase() + words.slice(1);
}
