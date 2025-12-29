import { motion } from "framer-motion";
import { Button } from "./ui/button";

interface TierCardProps {
  name: string;
  multiple: number;
  share: number;
  months: number;
  explanation: string;
  selected?: boolean;
  onSelect?: () => void;
  onExplain?: () => void;
}

export function TierCard({
  name,
  multiple,
  share,
  months,
  explanation,
  selected,
  onSelect,
  onExplain,
}: TierCardProps) {
  return (
    <motion.div
      whileHover={{ y: -6 }}
      className={`rounded-3xl border px-6 py-6 transition ${
        selected ? "border-indigo-400 bg-indigo-500/10" : "border-slate-800 bg-slate-900/60"
      }`}
    >
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold capitalize">{name} tier</h3>
        {selected && <span className="text-xs text-indigo-200">Selected</span>}
      </div>
      <div className="mt-4 grid gap-2 text-sm text-slate-200">
        <div>{multiple}x payout cap</div>
        <div>{share}% revenue share</div>
        <div>{months} month cap</div>
      </div>
      <p className="mt-4 text-xs text-slate-400">{explanation}</p>
      <div className="mt-6 flex gap-3">
        <Button variant="outline" onClick={onExplain}>
          Why these numbers
        </Button>
        <Button onClick={onSelect}>Choose tier</Button>
      </div>
    </motion.div>
  );
}
