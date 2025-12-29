import { useEffect, useState } from "react";
import { Card } from "../components/Card";
import { Button } from "../components/ui/button";
import { apiGet, apiPost } from "../lib/api";

interface ExitItem {
  exit_code: string;
  status: string;
  exit_type: string;
  settlement_method: string | null;
}

export default function FounderExits() {
  const [exits, setExits] = useState<ExitItem[]>([]);

  const load = () => {
    apiGet<ExitItem[]>("/founder/exits").then(setExits).catch(() => setExits([]));
  };

  useEffect(() => {
    load();
  }, []);

  const settle = async (exitCode: string, method: string) => {
    const id = Number(exitCode.split("-")[1]);
    await apiPost(`/founder/exits/${id}/settle`, { settlement_method: method });
    load();
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Exit requests</h2>
      <div className="grid gap-4">
        {exits.map((exit) => (
          <Card key={exit.exit_code} className="p-6">
            <div className="text-sm text-slate-400">{exit.exit_code}</div>
            <div className="mt-2 text-lg font-semibold">{exit.exit_type}</div>
            <div className="mt-2 text-xs text-slate-500">Status: {exit.status}</div>
            <div className="mt-4 flex gap-3">
              <Button onClick={() => settle(exit.exit_code, "cash")}>Settle with cash</Button>
              <Button variant="outline" onClick={() => settle(exit.exit_code, "loan")}>
                Offer loan referral
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
