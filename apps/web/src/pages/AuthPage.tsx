import { useState } from "react";
import { Button } from "../components/ui/button";
import { Card } from "../components/Card";
import { useAuth } from "../lib/auth";

interface AuthPageProps {
  onAuthed: (role: string) => void;
}

export default function AuthPage({ onAuthed }: AuthPageProps) {
  const { login, signup } = useAuth();
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("founder");
  const [country, setCountry] = useState("CA");
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    setError(null);
    try {
      if (mode === "signin") {
        await login(email, password);
      } else {
        await signup(email, password, role, country);
      }
      onAuthed(localStorage.getItem("role") ?? "founder");
    } catch {
      setError("Unable to authenticate. Check your credentials.");
    }
  };

  return (
    <div className="mx-auto max-w-3xl py-12">
      <Card className="p-10">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-semibold">Secure account access</h2>
          <div className="flex gap-3">
            <Button variant={mode === "signin" ? "default" : "outline"} onClick={() => setMode("signin")}>
              Sign in
            </Button>
            <Button variant={mode === "signup" ? "default" : "outline"} onClick={() => setMode("signup")}>
              Sign up
            </Button>
          </div>
        </div>
        <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
          Access is protected and sessions are validated server-side.
        </p>
        <div className="mt-6 space-y-4">
          <input
            className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 focus:outline-none dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 focus:outline-none dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100"
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {mode === "signup" && (
            <div className="grid gap-3 md:grid-cols-2">
              <select
                className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 focus:outline-none dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100"
                value={role}
                onChange={(e) => setRole(e.target.value)}
              >
                <option value="founder">Founder</option>
                <option value="investor">Investor</option>
              </select>
              <input
                className="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 focus:outline-none dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100"
                value={country}
                onChange={(e) => setCountry(e.target.value)}
              />
            </div>
          )}
          {error && <div className="text-sm text-slate-600 dark:text-slate-300">{error}</div>}
          <Button className="w-full" onClick={submit}>
            {mode === "signin" ? "Sign in" : "Create account"}
          </Button>
        </div>
      </Card>
    </div>
  );
}
