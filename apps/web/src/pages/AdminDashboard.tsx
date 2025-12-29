import { useEffect, useState } from "react";
import { Button } from "../components/ui/button";
import { Card } from "../components/Card";
import { StatusPill } from "../components/StatusPill";
import { apiGet, apiPost } from "../lib/api";

interface ApplicationItem {
  application_code: string;
  status: string;
  company_name: string;
}

interface RoundItem {
  round_code: string;
  status: string;
  selected_tier: string;
}

export default function AdminDashboard() {
  const [applications, setApplications] = useState<ApplicationItem[]>([]);
  const [rounds, setRounds] = useState<RoundItem[]>([]);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    apiGet<ApplicationItem[]>("/admin/applications").then(setApplications).catch(() => setApplications([]));
    apiGet<RoundItem[]>("/admin/rounds").then(setRounds).catch(() => setRounds([]));
  }, []);

  const runDistribution = async () => {
    await apiPost("/distributions/run-month", {});
    setMessage("Monthly distribution executed (demo).")
  };

  const createExit = async () => {
    await apiPost("/admin/demo/exit-request", { contract_id: 1, window: "quarterly" });
    setMessage("Exit request created (demo).")
  };

  const settleExit = async (settlement: "cash" | "loan") => {
    await apiPost("/admin/demo/settle-exit", { exit_request_id: 1, settlement });
    setMessage(`Exit settled with ${settlement} (demo).`)
  };

  return (
    <div className="space-y-8">
      <Card className="p-6">
        <h2 className="text-2xl font-semibold">Admin review queue</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {applications.map((app) => (
            <div key={app.application_code} className="rounded-2xl border border-slate-800 p-4">
              <div className="flex items-center justify-between">
                <div className="font-semibold">{app.company_name}</div>
                <StatusPill status={app.status} />
              </div>
              <div className="text-xs text-slate-400">{app.application_code}</div>
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-lg font-semibold">Rounds</h3>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          {rounds.map((round) => (
            <div key={round.round_code} className="rounded-2xl border border-slate-800 p-4">
              <div className="flex items-center justify-between">
                <div>{round.round_code}</div>
                <StatusPill status={round.status} />
              </div>
              <div className="text-xs text-slate-400">Tier: {round.selected_tier}</div>
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-lg font-semibold">Demo actions</h3>
        <p className="text-sm text-slate-400">Use these controls to simulate platform operations.</p>
        <div className="mt-4 flex flex-wrap gap-3">
          <Button onClick={runDistribution}>Run monthly distribution</Button>
          <Button variant="outline" onClick={createExit}>Create exit request</Button>
          <Button variant="ghost" onClick={() => settleExit("cash")}>Settle with cash</Button>
          <Button variant="ghost" onClick={() => settleExit("loan")}>Settle with loan referral</Button>
        </div>
        {message && <div className="mt-3 text-sm text-emerald-300">{message}</div>}
      </Card>
    </div>
  );
}
