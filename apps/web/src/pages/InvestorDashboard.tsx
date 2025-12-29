import { useEffect, useState } from "react";
import { Card } from "../components/Card";
import { Button } from "../components/ui/button";
import { ConfirmModal } from "../components/ConfirmModal";
import { apiGet, apiPost } from "../lib/api";

interface RoundSummary {
  round_code: string;
  startup_name: string;
  max_raise_cents: number;
  tier_selected: string;
  raised_cents: number;
}

interface RoundDetail {
  round_code: string;
  max_raise_cents: number;
  tier: {
    revenue_share_bps: number;
    time_cap_months: number;
    payout_cap_mult: number;
    min_hold_days: number;
    exit_fee_bps_quarterly: number;
    exit_fee_bps_offcycle: number;
  };
}

export default function InvestorDashboard() {
  const [rounds, setRounds] = useState<RoundSummary[]>([]);
  const [selected, setSelected] = useState<RoundDetail | null>(null);
  const [amount, setAmount] = useState(25000);
  const [complianceOpen, setComplianceOpen] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    apiGet<RoundSummary[]>("/investor/rounds").then(setRounds).catch(() => setRounds([]));
  }, []);

  const viewRound = async (roundCode: string) => {
    const id = Number(roundCode.split("-")[1]);
    const data = await apiGet<RoundDetail>(`/investor/rounds/${id}`);
    setSelected(data);
  };

  const invest = async () => {
    if (!selected) return;
    const id = Number(selected.round_code.split("-")[1]);
    await apiPost("/investor/invest", { round_id: id, amount_cents: amount });
    setMessage("Investment submitted. Check your portfolio for updates.");
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Discover rounds</h2>
      <div className="grid gap-6 lg:grid-cols-2">
        {rounds.map((round) => (
          <Card key={round.round_code} className="p-6">
            <div className="text-xs text-slate-400">Round {round.round_code}</div>
            <h3 className="mt-2 text-lg font-semibold">{round.startup_name}</h3>
            <p className="mt-3 text-sm text-slate-400">
              Raised ${(round.raised_cents / 100).toLocaleString()} / $
              {(round.max_raise_cents / 100).toLocaleString()} · Tier {round.tier_selected}
            </p>
            <Button className="mt-4" onClick={() => viewRound(round.round_code)}>
              View details
            </Button>
          </Card>
        ))}
      </div>

      {selected && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold">Round {selected.round_code}</h3>
          <div className="mt-4 grid gap-2 text-sm text-slate-400 md:grid-cols-3">
            <div>Revenue share: {selected.tier.revenue_share_bps / 100}%</div>
            <div>Time cap: {selected.tier.time_cap_months} months</div>
            <div>Payout cap: {selected.tier.payout_cap_mult}x</div>
            <div>Min hold: {selected.tier.min_hold_days} days</div>
            <div>Exit fee (quarterly): {selected.tier.exit_fee_bps_quarterly / 100}%</div>
            <div>Exit fee (off-cycle): {selected.tier.exit_fee_bps_offcycle / 100}%</div>
          </div>
          <div className="mt-4 flex items-center gap-3">
            <input
              className="rounded-2xl border border-slate-800 bg-slate-950 px-4 py-2 text-sm"
              value={amount}
              onChange={(e) => setAmount(Number(e.target.value))}
            />
            <Button onClick={() => setComplianceOpen(true)}>Invest</Button>
          </div>
          {message && <div className="mt-3 text-sm text-emerald-300">{message}</div>}
        </Card>
      )}

      <ConfirmModal
        open={complianceOpen}
        onOpenChange={setComplianceOpen}
        title="Compliance confirmation"
        description="Investments are subject to holding periods and payout caps. Projections are illustrative only."
        confirmLabel="Confirm investment"
        onConfirm={invest}
      />
    </div>
  );
}
