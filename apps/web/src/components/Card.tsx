import { PropsWithChildren } from "react";
import clsx from "clsx";

export function Card({ children, className }: PropsWithChildren<{ className?: string }>) {
  return (
    <div
      className={clsx(
        "rounded-3xl border border-slate-200/60 bg-white/70 shadow-card dark:border-slate-800 dark:bg-slate-900/60",
        className
      )}
    >
      {children}
    </div>
  );
}
