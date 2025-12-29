import clsx from "clsx";

const styles: Record<string, string> = {
  pending: "bg-amber-500/20 text-amber-200",
  approved: "bg-emerald-500/20 text-emerald-200",
  denied: "bg-rose-500/20 text-rose-200",
  published: "bg-indigo-500/20 text-indigo-200",
  draft: "bg-slate-500/20 text-slate-200",
  active: "bg-emerald-500/20 text-emerald-200",
  completed: "bg-slate-500/20 text-slate-200",
};

export function StatusPill({ status }: { status: string }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold",
        styles[status] ?? "bg-slate-500/20 text-slate-200"
      )}
    >
      {status}
    </span>
  );
}
