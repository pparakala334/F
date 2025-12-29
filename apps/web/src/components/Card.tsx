import { PropsWithChildren } from "react";
import clsx from "clsx";

export function Card({ children, className }: PropsWithChildren<{ className?: string }>) {
  return (
    <div className={clsx("rounded-3xl bg-slate-900/60 border border-slate-800 shadow-card", className)}>
      {children}
    </div>
  );
}
