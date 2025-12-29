import { useEffect, useState } from "react";
import { Card } from "../components/Card";
import { Button } from "../components/ui/button";
import { apiGet, apiPost } from "../lib/api";

interface ApplicationItem {
  application_code: string;
  status: string;
  startup_code: string;
  name: string;
  application_type: string;
  requested_limit_cents: number;
  documents: { doc_type: string; filename: string }[];
}

interface RoundItem {
  round_code: string;
  status: string;
  tier_selected: string | null;
}

export default function AdminDashboard() {
  const [applications, setApplications] = useState<ApplicationItem[]>([]);
  const [rounds, setRounds] = useState<RoundItem[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [exitCode, setExitCode] = useState("EXIT-0001");

  const load = () => {
    apiGet<ApplicationItem[]>("/admin/applications").then(setApplications).catch(() => setApplications([]));
    apiGet<RoundItem[]>("/admin/rounds").then(setRounds).catch(() => setRounds([]));
  };

  useEffect(() => {
    load();
  }, []);

  const approve = async (code: string) => {
    const id = Number(code.split("-")[1]);
    await apiPost(`/admin/applications/${id}/approve`, {});
    load();
  };

  const deny = async (code: string) => {
    const id = Number(code.split("-")[1]);
    await apiPost(`/admin/applications/${id}/deny`, {});
    load();
  };

  const runDistribution = async () => {
    await apiPost("/admin/distributions/run", { startup_id: 1, month: "2024-06-01" });
    setMessage("Distribution executed.");
  };

  const simulateRevenue = async () => {
    await apiPost("/admin/revenue/simulate", { startup_id: 1, month: "2024-06-01", gross_revenue_cents: 450000 });
    setMessage("Revenue simulated.");
  };

  const seed = async () => {
    await apiPost("/admin/demo/seed", {});
    setMessage("Seed data created.");
    load();
  };

  const settleExit = async (method: string) => {
    const id = Number(exitCode.split("-")[1]);
    await apiPost(`/admin/exits/${id}/settle?settlement_method=${method}`, {});
    setMessage(`Exit settled with ${method}.`);
  };

  return (
    <div className="space-y-8">
      <Card className="p-6">
        <h2 className="text-2xl font-semibold">Applications queue</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {applications.map((app) => (
            <div key={app.application_code} className="rounded-2xl border border-slate-200 dark:border-slate-800 p-4">
              <div className="text-sm text-slate-400">{app.application_code}</div>
              <div className="mt-2 text-lg font-semibold">{app.name}</div>
              <div className="text-xs text-slate-500 dark:text-slate-400">{app.application_type}</div>
              <div className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                {app.startup_code} · ${(app.requested_limit_cents / 100).toLocaleString()}
              </div>
              <div className="mt-2 text-xs text-slate-500 dark:text-slate-400">Status: {app.status}</div>
              <div className="mt-2 text-xs text-slate-500">
                Docs: {app.documents.map((doc) => doc.doc_type).join(", ") || "None"}
              </div>
              <div className="mt-3 flex gap-2">
                <Button onClick={() => approve(app.application_code)}>Approve</Button>
                <Button variant="outline" onClick={() => deny(app.application_code)}>
                  Deny
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-lg font-semibold">Rounds</h3>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {rounds.map((round) => (
            <div key={round.round_code} className="rounded-2xl border border-slate-200 dark:border-slate-800 p-4 text-sm text-slate-400">
              <div>{round.round_code}</div>
              <div>Status: {round.status}</div>
              <div>Tier: {round.tier_selected ?? "Not set"}</div>
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-lg font-semibold">Demo actions</h3>
        <div className="mt-4 flex flex-wrap gap-3">
          <Button onClick={seed}>Seed demo data</Button>
          <Button variant="outline" onClick={simulateRevenue}>
            Simulate revenue report
          </Button>
          <Button variant="outline" onClick={runDistribution}>
            Run monthly distribution
          </Button>
        </div>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <input
            className="rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950 px-4 py-2 text-sm"
            value={exitCode}
            onChange={(e) => setExitCode(e.target.value)}
          />
          <Button onClick={() => settleExit("cash")}>Settle exit (cash)</Button>
          <Button variant="outline" onClick={() => settleExit("loan")}>
            Settle exit (loan)
          </Button>
        </div>
        {message && <div className="mt-3 text-sm text-slate-500 dark:text-slate-400">{message}</div>}
      </Card>
    </div>
  );
}
