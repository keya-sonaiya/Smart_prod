interface MessageBubbleProps {
  role: "user" | "assistant";
  text: string;
}

export default function MessageBubble({ role, text }: MessageBubbleProps) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] whitespace-pre-wrap rounded-md px-3.5 py-2.5 text-[15px] leading-relaxed ${
          isUser
            ? "bg-pine text-paper"
            : "border border-line bg-surface text-ink"
        }`}
      >
        {text}
      </div>
    </div>
  );
}
