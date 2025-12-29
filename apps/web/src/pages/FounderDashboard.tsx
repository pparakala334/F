import { useEffect, useState } from "react";
import { Button } from "../components/ui/button";
import { Card } from "../components/Card";
import { StatusPill } from "../components/StatusPill";
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

export default function FounderDashboard() {
  const [tiers, setTiers] = useState<TierOption[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [publishDisclaimer, setPublishDisclaimer] = useState(false);
  const [modal, setModal] = useState<{ open: boolean; text: string }>({ open: false, text: "" });

  useEffect(() => {
    apiGet<TierOption[]>("/rounds/1/tiers").then(setTiers).catch(() => setTiers([]));
  }, []);

  const selectTier = async (tier: string) => {
    await apiPost(`/rounds/1/select-tier?tier=${tier}`, {});
    setSelected(tier);
  };

  const publish = async () => {
    setPublishDisclaimer(true);
    await apiPost("/rounds/1/publish", {});
  };

  return (
    <div className="space-y-8">
      <Card className="p-6">
        <h2 className="text-2xl font-semibold">Founder guided flow</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-5 text-sm">
          <div className="space-y-2">
            <div>Apply</div>
            <StatusPill status="approved" />
          </div>
          <div className="space-y-2">
            <div>Approval</div>
            <StatusPill status="approved" />
          </div>
          <div className="space-y-2">
            <div>Create round</div>
            <StatusPill status="draft" />
          </div>
          <div className="space-y-2">
            <div>Select tier</div>
            <StatusPill status={selected ? "approved" : "pending"} />
          </div>
          <div className="space-y-2">
            <div>Publish</div>
            <StatusPill status={selected ? "pending" : "draft"} />
          </div>
        </div>
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
            selected={tier.tier === selected}
            onSelect={() => selectTier(tier.tier)}
            onExplain={() => setModal({ open: true, text: tier.explanation })}
          />
        ))}
      </div>

      <Card className="p-6">
        <h3 className="text-lg font-semibold">Publish round</h3>
        <p className="mt-2 text-sm text-slate-400">
          Publishing your round makes it visible to investors. Projections are illustrative only.
        </p>
        <Button className="mt-4" onClick={publish}>
          Publish round
        </Button>
        {publishDisclaimer && (
          <div className="mt-3 text-xs text-slate-400">
            Disclaimer: This is not legal or financial advice. Payouts are not guaranteed.
          </div>
        )}
      </Card>

      <InfoModal
        open={modal.open}
        onOpenChange={(open) => setModal((prev) => ({ ...prev, open }))}
        title="Why these numbers"
        description={modal.text}
      />
    </div>
  );
}
