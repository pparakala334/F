import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Card } from "../components/Card";
import { Button } from "../components/ui/button";
import { StatusPill } from "../components/StatusPill";
import { ConfirmModal } from "../components/ConfirmModal";
import { TierCard } from "../components/TierCard";
import { apiGet, apiPost } from "../lib/api";

interface StartupDetail {
  id: number;
  legal_name: string;
  operating_name: string | null;
  country: string;
  industry: string;
  short_description: string;
}

interface ApplicationItem {
  application_code: string;
  id: number;
  name: string;
  application_type: string;
  created_at: string;
  submitted_at: string | null;
  reviewed_at: string | null;
  status: string;
}

interface ApplicationDetail {
  application_code: string;
  status: string;
  name: string;
  application_type: string;
  requested_limit_cents: number;
  risk_preference: string;
  admin_notes: string | null;
  startup_snapshot: { name: string; industry: string; country: string; short_description: string };
  documents: { doc_type: string; filename: string }[];
}

interface ApprovedApplication {
  application_code: string;
  id: number;
  name: string;
  application_type: string;
  approved_limit_cents: number;
  risk_preference: string;
  reviewed_at: string | null;
}

interface RoundItem {
  round_code: string;
  id: number;
  status: string;
  tier_selected: string | null;
  max_raise_cents: number;
  raised_cents: number;
  investor_count: number;
}

interface TierOption {
  tier: string;
  revenue_share_bps: number;
  time_cap_months: number;
  payout_cap_mult: number;
  min_hold_days: number;
  exit_fee_bps_quarterly: number;
  exit_fee_bps_offcycle: number;
  explanation_json: string;
}

interface RevenueReport {
  report_code: string;
  month: string;
  gross_revenue_cents: number;
  created_at: string;
  distribution_status: string;
  total_distributed_cents: number;
}

export default function FounderStartupDetail() {
  const { startupId } = useParams();
  const startup_id = Number(startupId);
  const [startup, setStartup] = useState<StartupDetail | null>(null);
  const [tab, setTab] = useState<"applications" | "publishing" | "revenue">("applications");
  const [applications, setApplications] = useState<ApplicationItem[]>([]);
  const [applicationDetail, setApplicationDetail] = useState<ApplicationDetail | null>(null);
  const [approvedApps, setApprovedApps] = useState<ApprovedApplication[]>([]);
  const [rounds, setRounds] = useState<RoundItem[]>([]);
  const [tiers, setTiers] = useState<TierOption[]>([]);
  const [selectedRound, setSelectedRound] = useState<number | null>(null);
  const [reports, setReports] = useState<RevenueReport[]>([]);
  const [submitModalOpen, setSubmitModalOpen] = useState(false);
  const [publishModalOpen, setPublishModalOpen] = useState(false);
  const [revenueModalOpen, setRevenueModalOpen] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [pendingApplicationId, setPendingApplicationId] = useState<number | null>(null);
  const [applicationForm, setApplicationForm] = useState({
    name: "Initial Funding Application",
    application_type: "Initial Funding Application",
    requested_limit_cents: 500000,
    risk_preference: "medium",
  });
  const [roundTitle, setRoundTitle] = useState("Revenue Share Round");
  const [revenueForm, setRevenueForm] = useState({ month: "2024-06", gross_revenue_cents: 200000 });
  const [docForm, setDocForm] = useState({ doc_type: "pitch_deck", filename: "pitch-deck.pdf" });

  const load = async () => {
    const startupData = await apiGet<StartupDetail>(`/founder/startups/${startup_id}`);
    setStartup(startupData);
    const apps = await apiGet<ApplicationItem[]>(`/founder/startups/${startup_id}/applications`);
    setApplications(apps);
    const approved = await apiGet<ApprovedApplication[]>(`/founder/startups/${startup_id}/applications/approved`);
    setApprovedApps(approved);
    const roundsData = await apiGet<RoundItem[]>(`/founder/startups/${startup_id}/rounds`);
    setRounds(roundsData);
    const reportsData = await apiGet<RevenueReport[]>(`/founder/revenue/${startup_id}`);
    setReports(reportsData);
  };

  useEffect(() => {
    load();
  }, [startup_id]);

  const createApplication = async () => {
    await apiPost(`/founder/startups/${startup_id}/applications`, applicationForm);
    await load();
  };

  const openApplication = async (id: number) => {
    const detail = await apiGet<ApplicationDetail>(`/founder/applications/${id}`);
    setApplicationDetail(detail);
  };

  const submitApplication = async (id: number) => {
    await apiPost(`/founder/applications/${id}/submit`, { fee_cents: 2500 });
    setMessage("Application submitted for review.");
    await load();
  };

  const createRound = async (applicationId: number) => {
    const round = await apiPost<{ id: number }>(`/founder/applications/${applicationId}/rounds`, {
      title: roundTitle,
    });
    setSelectedRound(round.id);
    await load();
  };

  const runTiers = async (roundId: number) => {
    await apiPost(`/founder/rounds/${roundId}/tiers`, { risk_level: "medium" });
    const data = await apiGet<TierOption[]>(`/founder/rounds/${roundId}/tiers`);
    setTiers(data);
    setSelectedRound(roundId);
  };

  const selectTier = async (roundId: number, tier: string) => {
    await apiPost(`/founder/rounds/${roundId}/select-tier?tier=${tier}`, {});
    await load();
  };

  const publishRound = async () => {
    if (!selectedRound) return;
    await apiPost(`/founder/rounds/${selectedRound}/publish`, {});
    setMessage("Round published.");
    await load();
  };

  const submitRevenue = async () => {
    await apiPost(`/founder/revenue/report`, {
      startup_id,
      month: `${revenueForm.month}-01`,
      gross_revenue_cents: revenueForm.gross_revenue_cents,
    });
    setMessage("Revenue reported.");
    await load();
  };

  const uploadDocument = async () => {
    const presign = await apiPost<{ upload_url: string }>(`/founder/documents/presign`, {
      startup_id,
      doc_type: docForm.doc_type,
      filename: docForm.filename,
    });
    await apiPost(`/founder/documents/complete`, {
      startup_id,
      doc_type: docForm.doc_type,
      filename: docForm.filename,
      storage_key: presign.upload_url,
    });
    setMessage(\"Document uploaded.\");
    await load();
  };

  return (
    <div className="space-y-8">
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold">{startup?.operating_name ?? startup?.legal_name}</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              {startup?.industry} · {startup?.country}
            </p>
          </div>
          <StatusPill status={"active"} />
        </div>
        <div className="mt-4 grid gap-4 text-sm text-slate-500 dark:text-slate-400 md:grid-cols-4">
          <div>Applications: {applications.length}</div>
          <div>
            Approved limits: $
            {(approvedApps.reduce((acc, app) => acc + app.approved_limit_cents, 0) / 100).toLocaleString()}
          </div>
          <div>Active rounds: {rounds.filter((r) => r.status === "published").length}</div>
          <div>Investors: {rounds.reduce((acc, r) => acc + r.investor_count, 0)}</div>
        </div>
      </Card>

      <div className="flex gap-3 text-sm">
        <Button variant={tab === "applications" ? "default" : "outline"} onClick={() => setTab("applications")}>Applications</Button>
        <Button variant={tab === "publishing" ? "default" : "outline"} onClick={() => setTab("publishing")}>Publishing</Button>
        <Button variant={tab === "revenue" ? "default" : "outline"} onClick={() => setTab("revenue")}>Revenue Reporting</Button>
      </div>

      {tab === "applications" && (
        <div className="space-y-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold">Supporting documents</h3>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <select
                className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
                value={docForm.doc_type}
                onChange={(e) => setDocForm({ ...docForm, doc_type: e.target.value })}
              >
                <option value="pitch_deck">Pitch deck (PDF)</option>
                <option value="incorporation_doc">Incorporation document (PDF)</option>
                <option value="revenue_report">Last 3 months revenue (CSV/PDF)</option>
              </select>
              <input
                className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
                value={docForm.filename}
                onChange={(e) => setDocForm({ ...docForm, filename: e.target.value })}
              />
            </div>
            <Button className="mt-4" onClick={uploadDocument}>Upload document</Button>
          </Card>
          <Card className="p-6">
            <h3 className="text-lg font-semibold">Create application</h3>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <input
                className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
                value={applicationForm.name}
                onChange={(e) => setApplicationForm({ ...applicationForm, name: e.target.value })}
              />
              <select
                className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
                value={applicationForm.application_type}
                onChange={(e) => setApplicationForm({ ...applicationForm, application_type: e.target.value })}
              >
                <option>Initial Funding Application</option>
                <option>Funding Limit Increase</option>
              </select>
              <input
                className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
                value={applicationForm.requested_limit_cents}
                onChange={(e) => setApplicationForm({ ...applicationForm, requested_limit_cents: Number(e.target.value) })}
              />
              <select
                className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
                value={applicationForm.risk_preference}
                onChange={(e) => setApplicationForm({ ...applicationForm, risk_preference: e.target.value })}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <Button className="mt-4" onClick={createApplication}>Save draft</Button>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold">Applications</h3>
            <div className="mt-4 grid gap-3">
              {applications.map((app) => (
                <div key={app.application_code} className="rounded-2xl border border-slate-200 p-4 text-sm dark:border-slate-800">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold">{app.name}</div>
                      <div className="text-xs text-slate-500 dark:text-slate-400">{app.application_type}</div>
                      <div className="text-xs text-slate-500 dark:text-slate-400">
                        Created {new Date(app.created_at).toLocaleDateString()} · Submitted {app.submitted_at ? new Date(app.submitted_at).toLocaleDateString() : "—"}
                      </div>
                      <div className="text-xs text-slate-500 dark:text-slate-400">
                        Reviewed {app.reviewed_at ? new Date(app.reviewed_at).toLocaleDateString() : "—"}
                      </div>
                    </div>
                    <StatusPill status={app.status} />
                  </div>
                  <div className="mt-3 flex gap-3">
                    <Button variant="outline" onClick={() => openApplication(app.id)}>View</Button>
                    {app.status === "draft" && (
                      <Button onClick={() => {
                          setPendingApplicationId(app.id);
                          setSubmitModalOpen(true);
                        }}>Submit</Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {applicationDetail && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold">{applicationDetail.name}</h3>
              <div className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                Requested ${(applicationDetail.requested_limit_cents / 100).toLocaleString()} · Risk {applicationDetail.risk_preference}
              </div>
              <div className="mt-3 text-sm text-slate-500 dark:text-slate-400">
                Documents: {applicationDetail.documents.map((doc) => doc.doc_type).join(", ") || "None"}
              </div>
              <div className="mt-4 text-sm text-slate-500 dark:text-slate-400">
                {applicationDetail.admin_notes ? `Admin notes: ${applicationDetail.admin_notes}` : "No admin notes."}
              </div>
            </Card>
          )}
        </div>
      )}

      {tab === "publishing" && (
        <div className="space-y-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold">Approved applications</h3>
            <div className="mt-4 grid gap-3">
              {approvedApps.map((app) => (
                <div key={app.application_code} className="rounded-2xl border border-slate-200 p-4 text-sm dark:border-slate-800">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold">{app.name}</div>
                      <div className="text-xs text-slate-500 dark:text-slate-400">Approved ${(app.approved_limit_cents / 100).toLocaleString()}</div>
                    </div>
                    <Button onClick={() => createRound(app.id)}>Create Round</Button>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold">Rounds</h3>
            <div className="mt-4 grid gap-3">
              {rounds.map((round) => (
                <div key={round.round_code} className="rounded-2xl border border-slate-200 p-4 text-sm dark:border-slate-800">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold">{round.round_code}</div>
                      <div className="text-xs text-slate-500 dark:text-slate-400">
                        Status: {round.status} · Tier {round.tier_selected ?? "—"}
                      </div>
                      <div className="text-xs text-slate-500 dark:text-slate-400">
                        Raised ${(round.raised_cents / 100).toLocaleString()} · Investors {round.investor_count}
                      </div>
                    </div>
                    {round.status === "draft" && (
                      <Button variant="outline" onClick={() => runTiers(round.id)}>Run tier algorithm</Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {tiers.length > 0 && selectedRound && (
            <div className="grid gap-6 lg:grid-cols-3">
              {tiers.map((tier) => (
                <TierCard
                  key={tier.tier}
                  name={tier.tier}
                  multiple={tier.payout_cap_mult}
                  share={tier.revenue_share_bps / 100}
                  months={tier.time_cap_months}
                  explanation={JSON.parse(tier.explanation_json).why}
                  onSelect={() => selectTier(selectedRound, tier.tier)}
                  onExplain={() => setMessage(JSON.parse(tier.explanation_json).why)}
                />
              ))}
            </div>
          )}

          {selectedRound && (
            <Card className="p-6">
              <Button onClick={() => setPublishModalOpen(true)}>Publish Round</Button>
            </Card>
          )}
        </div>
      )}

      {tab === "revenue" && (
        <div className="space-y-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold">Submit revenue</h3>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <input
                className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
                value={revenueForm.month}
                onChange={(e) => setRevenueForm({ ...revenueForm, month: e.target.value })}
              />
              <input
                className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
                value={revenueForm.gross_revenue_cents}
                onChange={(e) => setRevenueForm({ ...revenueForm, gross_revenue_cents: Number(e.target.value) })}
              />
            </div>
            <Button className="mt-4" onClick={() => setRevenueModalOpen(true)}>Submit revenue</Button>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold">Revenue reports</h3>
            <div className="mt-4 grid gap-3">
              {reports.map((report) => (
                <div key={report.report_code} className="rounded-2xl border border-slate-200 p-4 text-sm dark:border-slate-800">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-semibold">{report.month}</div>
                      <div className="text-xs text-slate-500 dark:text-slate-400">
                        ${(
                          report.gross_revenue_cents / 100
                        ).toLocaleString()} · Distributed ${(report.total_distributed_cents / 100).toLocaleString()}
                      </div>
                    </div>
                    <StatusPill status={report.distribution_status} />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}

      {message && <div className="text-sm text-slate-500 dark:text-slate-400">{message}</div>}

      <ConfirmModal
        open={publishModalOpen}
        onOpenChange={setPublishModalOpen}
        title="Publish round"
        description="Publishing makes your round visible to investors. Projections are illustrative only."
        confirmLabel="Publish"
        onConfirm={publishRound}
      />
      <ConfirmModal
        open={submitModalOpen}
        onOpenChange={setSubmitModalOpen}
        title="Submit application"
        description="Submitting sends your application to compliance review. Application fees apply."
        confirmLabel="Submit"
        onConfirm={() => pendingApplicationId && submitApplication(pendingApplicationId)}
      />
      <ConfirmModal
        open={revenueModalOpen}
        onOpenChange={setRevenueModalOpen}
        title="Submit revenue report"
        description="Reporting revenue creates a ledger entry and may trigger a distribution."
        confirmLabel="Submit"
        onConfirm={submitRevenue}
      />
    </div>
  );
}
