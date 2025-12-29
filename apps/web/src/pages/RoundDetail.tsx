import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card } from "../components/Card";
import { TierCard } from "../components/TierCard";
import { InfoModal } from "../components/InfoModal";
import { apiGet, apiPost } from "../lib/api";

interface TierOption {
  tier: string;
  multiple: number;
  revenue_share_percent: number;
  months: number;
  explanation: string;
}

export default function RoundDetail() {
  const { roundCode } = useParams();
  const roundId = useMemo(() => Number(roundCode?.split("-")[1] ?? 0), [roundCode]);
  const [tiers, setTiers] = useState<TierOption[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [showDisclaimer, setShowDisclaimer] = useState(false);
  const [modal, setModal] = useState<{ open: boolean; text: string }>({ open: false, text: "" });

  useEffect(() => {
    if (roundId) {
      apiGet<TierOption[]>(`/rounds/${roundId}/tiers`).then(setTiers).catch(() => setTiers([]));
    }
  }, [roundId]);

  const invest = async () => {
    setShowDisclaimer(true);
    await apiPost("/investments", { investor_id: 3, round_id: roundId, amount_cents: 25000 });
    setMessage("Investment submitted (demo). Check your portfolio.");
  };

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h2 className="text-2xl font-semibold">Round {roundCode}</h2>
        <p className="mt-2 text-sm text-slate-400">Projected outcomes are illustrative only.</p>
        <Button className="mt-4" onClick={invest}>
          Invest $250
        </Button>
        {showDisclaimer && (
          <div className="mt-4 text-xs text-slate-400">
            Disclaimer: This is not legal, financial, or investment advice. Returns are not guaranteed.
          </div>
        )}
        {message && <div className="mt-3 text-sm text-slate-500 dark:text-slate-400">{message}</div>}
      </Card>
      <div className="grid gap-6 lg:grid-cols-3">
        {tiers.map((tier) => (
          <TierCard
            key={tier.tier}
            name={tier.tier}
            multiple={tier.multiple}
            share={tier.revenue_share_percent}
            months={tier.months}
            explanation={tier.explanation}
            onSelect={() => setMessage(`Selected ${tier.tier} tier (demo).`)}
            onExplain={() => setModal({ open: true, text: tier.explanation })}
          />
        ))}
      </div>
      <InfoModal
        open={modal.open}
        onOpenChange={(open) => setModal((prev) => ({ ...prev, open }))}
        title="Why these numbers"
        description={modal.text}
      />
    </div>
  );
}
