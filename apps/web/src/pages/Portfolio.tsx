import { useEffect, useState } from "react";
import { Button } from "../components/ui/button";
import { Card } from "../components/Card";
import { StatusPill } from "../components/StatusPill";
import { apiGet } from "../lib/api";

interface PortfolioItem {
  investment_code: string;
  startup_name: string;
  amount_cents: number;
  status: string;
}

export default function Portfolio() {
  const [items, setItems] = useState<PortfolioItem[]>([]);
  const [disclaimer, setDisclaimer] = useState(false);

  useEffect(() => {
    apiGet<PortfolioItem[]>("/investments/portfolio/3").then(setItems).catch(() => setItems([]));
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Investor portfolio</h2>
      <div className="grid gap-6 lg:grid-cols-2">
        {items.map((item) => (
          <Card key={item.investment_code} className="p-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">{item.startup_name}</h3>
              <StatusPill status={item.status} />
            </div>
            <p className="mt-2 text-sm text-slate-400">{item.investment_code}</p>
            <div className="mt-4 text-sm text-slate-300">
              Invested ${(item.amount_cents / 100).toLocaleString()}
            </div>
            <Button className="mt-4" onClick={() => setDisclaimer(true)}>
              Request exit
            </Button>
            {disclaimer && (
              <div className="mt-3 text-xs text-slate-400">
                Disclaimer: Exit requests may incur fees and are subject to minimum holding periods.
              </div>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
