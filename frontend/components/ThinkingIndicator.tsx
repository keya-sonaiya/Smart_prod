export default function ThinkingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="flex items-center gap-1.5 rounded-md border border-line bg-surface px-3.5 py-3">
        <span className="thinking-dot h-1.5 w-1.5 rounded-full bg-inksoft [animation-delay:0ms]" />
        <span className="thinking-dot h-1.5 w-1.5 rounded-full bg-inksoft [animation-delay:150ms]" />
        <span className="thinking-dot h-1.5 w-1.5 rounded-full bg-inksoft [animation-delay:300ms]" />
      </div>
    </div>
  );
}
