import { useEffect, useState } from "react";
import { Card } from "../components/Card";
import { apiGet } from "../lib/api";

interface LedgerEntry {
  entry_code: string;
  type: string;
  amount_cents: number;
}

export default function AdminLedger() {
  const [entries, setEntries] = useState<LedgerEntry[]>([]);

  useEffect(() => {
    apiGet<LedgerEntry[]>("/admin/ledger").then(setEntries).catch(() => setEntries([]));
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Ledger</h2>
      <div className="grid gap-4">
        {entries.map((entry) => (
          <Card key={entry.entry_code} className="p-4">
            <div className="flex items-center justify-between text-sm text-slate-400">
              <span>{entry.entry_code}</span>
              <span>{entry.type}</span>
            </div>
            <div className="mt-2 text-lg font-semibold">${(entry.amount_cents / 100).toLocaleString()}</div>
          </Card>
        ))}
      </div>
    </div>
  );
}
