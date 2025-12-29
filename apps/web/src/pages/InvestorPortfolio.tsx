import { useEffect, useState } from "react";
import { Card } from "../components/Card";
import { apiGet } from "../lib/api";

interface PortfolioItem {
  investment_code: string;
  contract_code: string | null;
  amount_cents: number;
  status: string;
  paid_to_date_cents: number;
  payout_cap_cents: number;
}

export default function InvestorPortfolio() {
  const [items, setItems] = useState<PortfolioItem[]>([]);

  useEffect(() => {
    apiGet<PortfolioItem[]>("/investor/portfolio").then(setItems).catch(() => setItems([]));
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Portfolio</h2>
      <div className="grid gap-6 md:grid-cols-2">
        {items.map((item) => (
          <Card key={item.investment_code} className="p-6">
            <div className="text-xs text-slate-400">{item.investment_code}</div>
            {item.contract_code && <div className="text-xs text-slate-500">{item.contract_code}</div>}
            <div className="mt-2 text-lg font-semibold">${(item.amount_cents / 100).toLocaleString()}</div>
            <div className="mt-3 text-sm text-slate-400">
              Paid to date ${(item.paid_to_date_cents / 100).toLocaleString()} · Cap $
              {(item.payout_cap_cents / 100).toLocaleString()}
            </div>
            <div className="mt-2 text-xs text-slate-500">Status: {item.status}</div>
          </Card>
        ))}
      </div>
    </div>
  );
}
