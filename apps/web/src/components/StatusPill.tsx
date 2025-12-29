import clsx from "clsx";

const styles: Record<string, string> = {
  pending: "bg-charcoal/10 text-charcoal dark:bg-cream/10 dark:text-cream",
  approved: "bg-charcoal/10 text-charcoal dark:bg-cream/10 dark:text-cream",
  denied: "bg-charcoal/10 text-charcoal dark:bg-cream/10 dark:text-cream",
  published: "bg-charcoal/10 text-charcoal dark:bg-cream/10 dark:text-cream",
  draft: "bg-charcoal/10 text-charcoal dark:bg-cream/10 dark:text-cream",
  active: "bg-charcoal/10 text-charcoal dark:bg-cream/10 dark:text-cream",
  completed: "bg-charcoal/10 text-charcoal dark:bg-cream/10 dark:text-cream",
};

export function StatusPill({ status, label }: { status: string; label?: string }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold",
        styles[status] ?? "bg-slate-500/20 text-slate-200"
      )}
    >
      {label ?? status}
    </span>
  );
}
