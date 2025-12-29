import { useEffect, useState } from "react";
import { Button } from "../components/ui/button";
import { Card } from "../components/Card";
import { useAuth } from "../lib/auth";
import { apiGet } from "../lib/api";

interface OktaConfig {
  enabled: boolean;
  issuer?: string | null;
  client_id?: string | null;
}

export default function Login() {
  const auth = useAuth();
  const [email, setEmail] = useState("admin@demo.com");
  const [password, setPassword] = useState("password");
  const [okta, setOkta] = useState<OktaConfig>({ enabled: false });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet<OktaConfig>("/auth/okta/config").then(setOkta).catch(() => setOkta({ enabled: false }));
  }, []);

  const handleLogin = async () => {
    setError(null);
    try {
      await auth.login(email, password);
    } catch (err) {
      setError("Unable to login. Check demo credentials.");
    }
  };

  return (
    <Card className="mx-auto max-w-xl p-8">
      <h2 className="text-2xl font-semibold">Login</h2>
      <p className="mt-2 text-sm text-slate-400">
        {okta.enabled ? "Okta is enabled. Use your SSO account." : "Demo login with email + password."}
      </p>
      <div className="mt-6 space-y-4">
        <input
          className="w-full rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950 px-4 py-3 text-sm"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
        />
        <input
          type="password"
          className="w-full rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950 px-4 py-3 text-sm"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
        />
        {error && <div className="text-sm text-slate-600 dark:text-slate-300">{error}</div>}
        <div className="flex gap-3">
          <Button onClick={handleLogin}>Login</Button>
          {okta.enabled && <Button variant="outline">Continue with Okta</Button>}
        </div>
        <div className="text-xs text-slate-500">
          Demo accounts: admin@demo.com, founder@demo.com, investor@demo.com (password: password)
        </div>
      </div>
    </Card>
  );
}
