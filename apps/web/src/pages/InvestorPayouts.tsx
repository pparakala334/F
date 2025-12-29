import { useEffect, useState } from "react";
import { Card } from "../components/Card";
import { apiGet } from "../lib/api";

interface PayoutItem {
  payout_code: string;
  amount_cents: number;
  created_at: string;
}

export default function InvestorPayouts() {
  const [items, setItems] = useState<PayoutItem[]>([]);

  useEffect(() => {
    apiGet<PayoutItem[]>("/investor/payouts").then(setItems).catch(() => setItems([]));
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Payout history</h2>
      <div className="grid gap-4">
        {items.map((item) => (
          <Card key={item.payout_code} className="p-4">
            <div className="flex items-center justify-between text-sm text-slate-400">
              <span>{item.payout_code}</span>
              <span>{new Date(item.created_at).toLocaleDateString()}</span>
            </div>
            <div className="mt-2 text-lg font-semibold">${(item.amount_cents / 100).toLocaleString()}</div>
          </Card>
        ))}
      </div>
    </div>
  );
}
