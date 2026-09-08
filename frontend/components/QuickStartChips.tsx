interface QuickStartChipsProps {
  onPick: (message: string) => void;
  disabled: boolean;
}

const STARTERS = [
  "I want to build a dining table.",
  "I want to mount my TV on the wall.",
  "I want to furnish my living room.",
  "I want to build a gaming PC.",
];

export default function QuickStartChips({ onPick, disabled }: QuickStartChipsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {STARTERS.map((text) => (
        <button
          key={text}
          type="button"
          disabled={disabled}
          onClick={() => onPick(text)}
          className="rounded-full border border-line bg-surface px-3.5 py-1.5 text-sm text-inksoft transition-colors hover:border-pine hover:text-pine disabled:cursor-not-allowed disabled:opacity-50"
        >
          {text}
        </button>
      ))}
    </div>
  );
}
