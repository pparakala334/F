import { PropsWithChildren } from "react";
import { DarkModeToggle } from "../components/DarkModeToggle";
import { Button } from "../components/ui/button";

interface AppShellProps {
  companyName: string;
  onSignIn?: () => void;
  showPublicNav?: boolean;
}

const publicNav = [
  { href: "#product", label: "Product" },
  { href: "#how", label: "How it works" },
  { href: "#pricing", label: "Pricing" },
  { href: "#safety", label: "Safety" },
  { href: "#faq", label: "FAQ" },
];

export function AppShell({ children, companyName, onSignIn, showPublicNav }: PropsWithChildren<AppShellProps>) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-950 to-slate-900 text-slate-100">
      <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-6">
            <span className="text-lg font-semibold">{companyName}</span>
            {showPublicNav && (
              <nav className="hidden gap-4 md:flex">
                {publicNav.map((item) => (
                  <a key={item.href} href={item.href} className="text-sm text-slate-400 hover:text-white">
                    {item.label}
                  </a>
                ))}
                <button onClick={onSignIn} className="text-sm text-slate-200 hover:text-white">
                  Sign in
                </button>
              </nav>
            )}
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
