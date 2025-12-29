import { PropsWithChildren } from "react";
import { Link } from "react-router-dom";
import { DarkModeToggle } from "../components/DarkModeToggle";
import { Button } from "../components/ui/button";
import { useAuth } from "../lib/auth";

interface AppShellProps {
  companyName: string;
  onSignIn?: () => void;
  showPublicNav?: boolean;
}

export function AppShell({ children, companyName, onSignIn, showPublicNav }: PropsWithChildren<AppShellProps>) {
  const auth = useAuth();
  const homeLink = auth.role ? `/app/${auth.role}` : "/";
  return (
    <div className="min-h-screen bg-cream text-slate-900 dark:bg-charcoal dark:text-slate-100">
      <header className="sticky top-0 z-50 border-b border-slate-200 bg-cream/80 backdrop-blur dark:border-slate-800 dark:bg-charcoal/80">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-6">
            <Link to={homeLink} className="text-lg font-semibold">
              {companyName}
            </Link>
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
