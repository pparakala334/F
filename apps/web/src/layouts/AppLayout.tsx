import { PropsWithChildren, useEffect } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { DarkModeToggle } from "../components/DarkModeToggle";
import { useAuth } from "../lib/auth";

interface AppLayoutProps {
  role: string;
  companyName: string;
}

const navItems: Record<string, { to: string; label: string }[]> = {
  founder: [
    { to: "/app/founder", label: "Dashboard" },
    { to: "/app/founder/exits", label: "Exits" },
  ],
  investor: [
    { to: "/app/investor", label: "Discover" },
    { to: "/app/investor/portfolio", label: "Portfolio" },
    { to: "/app/investor/exits", label: "Exits" },
    { to: "/app/investor/payouts", label: "Payouts" },
  ],
  admin: [
    { to: "/app/admin", label: "Operations" },
    { to: "/app/admin/ledger", label: "Ledger" },
  ],
};

export function AppLayout({ children, role, companyName }: PropsWithChildren<AppLayoutProps>) {
  const auth = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!auth.token) {
      navigate("/");
      return;
    }
    if (auth.role && auth.role !== role) {
      navigate("/");
    }
  }, [auth.role, auth.token, role, navigate]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="flex">
        <aside className="hidden min-h-screen w-64 border-r border-slate-800 bg-slate-950/80 p-6 md:block">
          <div className="text-lg font-semibold">{companyName}</div>
          <nav className="mt-8 space-y-2 text-sm">
            {navItems[role]?.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `block rounded-xl px-3 py-2 ${isActive ? "bg-slate-800 text-white" : "text-slate-400"}`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </aside>
        <div className="flex-1">
          <header className="flex items-center justify-between border-b border-slate-800 bg-slate-950/80 px-6 py-4">
            <div className="text-sm text-slate-400">Welcome back</div>
            <DarkModeToggle />
          </header>
          <main className="px-6 py-8">{children}</main>
        </div>
      </div>
    </div>
  );
}
