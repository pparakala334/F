import { useEffect, useState } from "react";
import { Card } from "../components/Card";
import { Button } from "../components/ui/button";
import { TierCard } from "../components/TierCard";
import { InfoModal } from "../components/InfoModal";
import { ConfirmModal } from "../components/ConfirmModal";
import { apiGet, apiPost } from "../lib/api";

interface Startup {
  id: number;
  name: string;
  description: string;
  country: string;
  website?: string;
}

interface Application {
  application_code: string;
  status: string;
}

interface Round {
  id: number;
  round_code: string;
  status: string;
  tier_selected: string | null;
  max_raise_cents: number;
  raised_cents: number;
}

interface TierOption {
  tier: string;
  revenue_share_bps: number;
  time_cap_months: number;
  payout_cap_mult: number;
  min_hold_days: number;
  explanation_json: string;
}

export default function FounderDashboard() {
  const [startup, setStartup] = useState<Startup | null>(null);
  const [application, setApplication] = useState<Application | null>(null);
  const [rounds, setRounds] = useState<Round[]>([]);
  const [tiers, setTiers] = useState<TierOption[]>([]);
  const [selectedRound, setSelectedRound] = useState<number | null>(null);
  const [modal, setModal] = useState<{ open: boolean; text: string }>({ open: false, text: "" });
  const [publishOpen, setPublishOpen] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    apiGet<Startup | null>("/founder/startup").then(setStartup).catch(() => setStartup(null));
    apiGet<Application | null>("/founder/application").then(setApplication).catch(() => setApplication(null));
    apiGet<Round[]>("/founder/rounds").then(setRounds).catch(() => setRounds([]));
  }, []);

  const createStartup = async () => {
    await apiPost("/founder/startup", {
      name: "Northlake Labs",
      description: "AI workflow infrastructure",
      country: "CA",
      website: "https://northlake.example",
    });
    const data = await apiGet<Startup | null>("/founder/startup");
    setStartup(data);
  };

  const submitApplication = async () => {
    if (!startup) return;
    await apiPost("/founder/application/submit", { startup_id: startup.id, fee_cents: 2500 });
    const data = await apiGet<Application | null>("/founder/application");
    setApplication(data);
  };

  const uploadDocs = async () => {
    if (!startup) return;
    const presign = await apiPost<{ upload_url: string }>("/founder/documents/presign", {
      filename: "pitch_deck.pdf",
      doc_type: "pitch_deck",
    });
    await apiPost("/founder/documents/complete", {
      startup_id: startup.id,
      filename: "pitch_deck.pdf",
      doc_type: "pitch_deck",
      storage_key: presign.upload_url,
    });
    setMessage("Documents uploaded.");
  };

  const createRound = async () => {
    if (!startup) return;
    await apiPost("/founder/rounds", {
      startup_id: startup.id,
      title: "Revenue Share Round",
      max_raise_cents: 2000000,
    });
    const data = await apiGet<Round[]>("/founder/rounds");
    setRounds(data);
  };

  const runTiers = async (roundId: number) => {
    await apiPost(`/founder/rounds/${roundId}/tiers`, { risk_level: "medium" });
    const data = await apiGet<TierOption[]>(`/founder/rounds/${roundId}/tiers`);
    setTiers(data);
    setSelectedRound(roundId);
  };

  const selectTier = async (tier: string) => {
    if (!selectedRound) return;
    await apiPost(`/founder/rounds/${selectedRound}/select-tier?tier=${tier}`, {});
    setMessage(`Selected ${tier} tier.`);
    const data = await apiGet<Round[]>("/founder/rounds");
    setRounds(data);
  };

  const publishRound = async () => {
    if (!selectedRound) return;
    await apiPost(`/founder/rounds/${selectedRound}/publish`, {});
    setMessage("Round published.");
    const data = await apiGet<Round[]>("/founder/rounds");
    setRounds(data);
  };

  const reportRevenue = async () => {
    if (!startup) return;
    await apiPost("/founder/revenue/report", {
      startup_id: startup.id,
      month: "2024-06-01",
      gross_revenue_cents: 450000,
    });
    setMessage("Revenue reported for June.");
  };

  return (
    <div className="space-y-8">
      <Card className="p-6">
        <h2 className="text-2xl font-semibold">Founder workflow</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-4 text-sm text-slate-400">
          <div>Startup profile: {startup ? "Complete" : "Pending"}</div>
          <div>Application: {application?.status ?? "Pending"}</div>
          <div>Round draft: {rounds.length > 0 ? "Created" : "Pending"}</div>
          <div>Publish: {rounds.some((round) => round.status === "published") ? "Live" : "Pending"}</div>
        </div>
      </Card>

      <Card className="p-6 space-y-4">
        <h3 className="text-lg font-semibold">1. Startup profile</h3>
        <Button onClick={createStartup}>Create startup profile</Button>
      </Card>

      <Card className="p-6 space-y-4">
        <h3 className="text-lg font-semibold">2. Application</h3>
        <Button onClick={submitApplication}>Submit application + fee</Button>
      </Card>

      <Card className="p-6 space-y-4">
        <h3 className="text-lg font-semibold">3. Upload documents</h3>
        <Button onClick={uploadDocs}>Upload required docs</Button>
      </Card>

      <Card className="p-6 space-y-4">
        <h3 className="text-lg font-semibold">4. Round draft</h3>
        <Button onClick={createRound}>Create draft round</Button>
        <div className="grid gap-3 md:grid-cols-2">
          {rounds.map((round) => (
            <div key={round.round_code} className="rounded-2xl border border-slate-800 p-4 text-sm text-slate-400">
              <div>{round.round_code}</div>
              <div>Status: {round.status}</div>
              <div>
                Raised ${(round.raised_cents / 100).toLocaleString()} / $
                {(round.max_raise_cents / 100).toLocaleString()}
              </div>
              <Button className="mt-2" onClick={() => runTiers(round.id)}>
                Run tier algorithm
              </Button>
            </div>
          ))}
        </div>
      </Card>

      {tiers.length > 0 && (
        <div className="grid gap-6 lg:grid-cols-3">
          {tiers.map((tier) => (
            <TierCard
              key={tier.tier}
              name={tier.tier}
              multiple={tier.payout_cap_mult}
              share={tier.revenue_share_bps / 100}
              months={tier.time_cap_months}
              explanation={JSON.parse(tier.explanation_json).why}
              onSelect={() => selectTier(tier.tier)}
              onExplain={() => setModal({ open: true, text: JSON.parse(tier.explanation_json).why })}
            />
          ))}
        </div>
      )}

      <Card className="p-6 space-y-4">
        <h3 className="text-lg font-semibold">5. Publish</h3>
        <Button onClick={() => setPublishOpen(true)}>Publish selected round</Button>
      </Card>

      <Card className="p-6 space-y-4">
        <h3 className="text-lg font-semibold">6. Revenue reporting</h3>
        <Button onClick={reportRevenue}>Report monthly revenue</Button>
      </Card>

      {message && <div className="text-sm text-emerald-300">{message}</div>}

      <InfoModal
        open={modal.open}
        onOpenChange={(open) => setModal((prev) => ({ ...prev, open }))}
        title="Why these numbers"
        description={modal.text}
      />
      <ConfirmModal
        open={publishOpen}
        onOpenChange={setPublishOpen}
        title="Publish confirmation"
        description="Publishing makes your round visible to investors. Projections are illustrative only."
        confirmLabel="Confirm publish"
        onConfirm={publishRound}
      />
    </div>
  );
}
