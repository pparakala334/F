import { PropsWithChildren } from "react";
import { NavLink } from "react-router-dom";
import { DarkModeToggle } from "../components/DarkModeToggle";

interface AppShellProps {
  role?: string | null;
  companyName: string;
}

const baseNav = [
  { to: "/", label: "Landing" },
  { to: "/discover", label: "Discover" },
  { to: "/disclaimer", label: "Disclaimer" },
];

const roleNav: Record<string, { to: string; label: string }[]> = {
  founder: [
    { to: "/founder", label: "Founder" },
    { to: "/rounds", label: "My Rounds" },
  ],
  investor: [
    { to: "/portfolio", label: "Portfolio" },
    { to: "/discover", label: "Discover" },
  ],
  admin: [
    { to: "/admin", label: "Admin" },
  ],
  service_provider: [
    { to: "/providers", label: "Providers" },
  ],
};

export function AppShell({ children, role, companyName }: PropsWithChildren<AppShellProps>) {
  const nav = [...baseNav, ...(role ? roleNav[role] ?? [] : [])];

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-950 to-slate-900 text-slate-100">
      <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <span className="text-lg font-semibold">{companyName}</span>
            <nav className="hidden gap-4 md:flex">
              {nav.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `text-sm ${isActive ? "text-white" : "text-slate-400"}`
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>
          <DarkModeToggle />
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-10">{children}</main>
    </div>
  );
}
