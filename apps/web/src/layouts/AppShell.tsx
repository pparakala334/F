import { PropsWithChildren } from "react";
import { DarkModeToggle } from "../components/DarkModeToggle";
import { Button } from "../components/ui/button";

interface AppShellProps {
  companyName: string;
  onSignIn?: () => void;
  showPublicNav?: boolean;
}

export function AppShell({ children, companyName, onSignIn, showPublicNav }: PropsWithChildren<AppShellProps>) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-cream via-cream to-slate-100 text-slate-900 dark:from-charcoal dark:via-charcoal dark:to-slate-950 dark:text-slate-100">
      <header className="sticky top-0 z-50 border-b border-slate-200 bg-cream/80 backdrop-blur dark:border-slate-800 dark:bg-charcoal/80">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-6">
            <span className="text-lg font-semibold">{companyName}</span>
          </div>
          <div className="flex items-center gap-3">
            {showPublicNav && (
              <Button onClick={onSignIn} variant="outline">
                Sign in
              </Button>
            )}
            <DarkModeToggle />
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-10">{children}</main>
    </div>
  );
}
