import * as Dialog from "@radix-ui/react-dialog";
import { useState } from "react";
import { Button } from "./ui/button";
import { useAuth } from "../lib/auth";

interface AuthModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onAuthed: (role: string) => void;
}

export function AuthModal({ open, onOpenChange, onAuthed }: AuthModalProps) {
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
        onAuthed(localStorage.getItem("role") ?? "founder");
      } else {
        await signup(email, password, role, country);
        onAuthed(localStorage.getItem("role") ?? "founder");
      }
      onOpenChange(false);
    } catch {
      setError("Unable to authenticate. Check your credentials.");
    }
  };

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-slate-950/70" />
        <Dialog.Content className="fixed left-1/2 top-1/2 w-[90%] max-w-lg -translate-x-1/2 -translate-y-1/2 rounded-3xl border border-slate-800 bg-slate-950 p-6">
          <Dialog.Title className="text-lg font-semibold">Access your account</Dialog.Title>
          <div className="mt-4 flex gap-3">
            <Button variant={mode === "signin" ? "default" : "outline"} onClick={() => setMode("signin")}>
              Sign in
            </Button>
            <Button variant={mode === "signup" ? "default" : "outline"} onClick={() => setMode("signup")}>
              Sign up
            </Button>
          </div>
          <div className="mt-6 space-y-3">
            <input
              className="w-full rounded-2xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <input
              className="w-full rounded-2xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm"
              placeholder="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            {mode === "signup" && (
              <div className="grid gap-3 md:grid-cols-2">
                <select
                  className="rounded-2xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                >
                  <option value="founder">Founder</option>
                  <option value="investor">Investor</option>
                </select>
                <input
                  className="rounded-2xl border border-slate-800 bg-slate-950 px-4 py-3 text-sm"
                  value={country}
                  onChange={(e) => setCountry(e.target.value)}
                />
              </div>
            )}
            {error && <div className="text-sm text-rose-400">{error}</div>}
            <Button className="w-full" onClick={submit}>
              {mode === "signin" ? "Sign in" : "Create account"}
            </Button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
