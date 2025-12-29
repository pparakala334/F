import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "../components/Card";
import { Button } from "../components/ui/button";
import { StatusPill } from "../components/StatusPill";
import { apiGet, apiPost } from "../lib/api";

interface StartupSummary {
  startup_code: string;
  id: number;
  name: string;
  industry: string;
  country: string;
  status: string;
  total_raised_cents: number;
  active_round: boolean;
  last_revenue_reported: string | null;
}

export default function FounderStartups() {
  const [startups, setStartups] = useState<StartupSummary[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    legal_name: "",
    operating_name: "",
    country: "CA",
    incorporation_type: "Corp",
    incorporation_date: "",
    website: "",
    logo_key: "",
    industry: "Fintech",
    sub_industry: "",
    short_description: "",
    long_description: "",
    current_monthly_revenue: "$0-$10k",
    revenue_model: "SaaS",
    revenue_consistency: "Early",
    revenue_stage: "Early",
    existing_debt: false,
    existing_investors: false,
    intended_use_of_funds: ["Growth"],
    target_funding_size: "$250k-$1M",
    preferred_timeline: "3-6 months",
  });
  const navigate = useNavigate();
  const countryMode = import.meta.env.VITE_COUNTRY_MODE ?? "CA";

  const load = () => {
    apiGet<StartupSummary[]>("/founder/startups").then(setStartups).catch(() => setStartups([]));
  };

  useEffect(() => {
    load();
  }, []);

  const createStartup = async () => {
    await apiPost("/founder/startups", form);
    setShowForm(false);
    load();
  };

  if (startups.length === 0 && !showForm) {
    return (
      <Card className="mx-auto max-w-2xl p-10 text-center">
        <h2 className="text-2xl font-semibold">Create your first startup profile</h2>
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
          Set up your company once. Apply for funding when ready.
        </p>
        <Button className="mt-6" onClick={() => setShowForm(true)}>
          Create Startup
        </Button>
      </Card>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Startups</h2>
        <Button variant="outline" onClick={() => setShowForm((prev) => !prev)}>
          {showForm ? "Close" : "Create Startup"}
        </Button>
      </div>

      {showForm && (
        <Card className="p-8">
          <h3 className="text-lg font-semibold">Startup profile</h3>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <input
              className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
              placeholder="Legal Company Name"
              value={form.legal_name}
              onChange={(e) => setForm({ ...form, legal_name: e.target.value })}
            />
            <input
              className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
              placeholder="Operating Name"
              value={form.operating_name}
              onChange={(e) => setForm({ ...form, operating_name: e.target.value })}
            />
            <input
              className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
              placeholder="Country"
              value={countryMode === "CA" ? "CA" : form.country}
              disabled={countryMode === "CA"}
              onChange={(e) => setForm({ ...form, country: e.target.value })}
            />
            <select
              className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
              value={form.incorporation_type}
              onChange={(e) => setForm({ ...form, incorporation_type: e.target.value })}
            >
              <option value="Corp">Corp</option>
              <option value="LLC">LLC</option>
              <option value="Sole Prop">Sole Prop</option>
              <option value="Other">Other</option>
            </select>
            <input
              className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
              placeholder="Incorporation Date (YYYY-MM-DD)"
              value={form.incorporation_date}
              onChange={(e) => setForm({ ...form, incorporation_date: e.target.value })}
            />
            <input
              className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
              placeholder="Website"
              value={form.website}
              onChange={(e) => setForm({ ...form, website: e.target.value })}
            />
            <input
              className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
              placeholder="Logo key (optional)"
              value={form.logo_key}
              onChange={(e) => setForm({ ...form, logo_key: e.target.value })}
            />
            <input
              className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
              placeholder="Industry"
              value={form.industry}
              onChange={(e) => setForm({ ...form, industry: e.target.value })}
            />
            <input
              className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
              placeholder="Sub-industry"
              value={form.sub_industry}
              onChange={(e) => setForm({ ...form, sub_industry: e.target.value })}
            />
            <input
              className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
              placeholder="Short description"
              value={form.short_description}
              onChange={(e) => setForm({ ...form, short_description: e.target.value })}
            />
            <textarea
              className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950 md:col-span-2"
              placeholder="Long description"
              value={form.long_description}
              onChange={(e) => setForm({ ...form, long_description: e.target.value })}
            />
            <select
              className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
              value={form.current_monthly_revenue}
              onChange={(e) => setForm({ ...form, current_monthly_revenue: e.target.value })}
            >
              <option value="$0-$10k">$0-$10k</option>
              <option value="$10k-$25k">$10k-$25k</option>
              <option value="$25k-$50k">$25k-$50k</option>
              <option value="$50k+">$50k+</option>
            </select>
            <select
              className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
              value={form.revenue_model}
              onChange={(e) => setForm({ ...form, revenue_model: e.target.value })}
            >
              <option value="SaaS">SaaS</option>
              <option value="Services">Services</option>
              <option value="Marketplace">Marketplace</option>
              <option value="Other">Other</option>
            </select>
            <select
              className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
              value={form.revenue_consistency}
              onChange={(e) => setForm({ ...form, revenue_consistency: e.target.value })}
            >
              <option value="Pre-revenue">Pre-revenue</option>
              <option value="Early">Early</option>
              <option value="Stable">Stable</option>
            </select>
            <select
              className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
              value={form.existing_debt ? "yes" : "no"}
              onChange={(e) => setForm({ ...form, existing_debt: e.target.value === "yes" })}
            >
              <option value="no">Existing debt: No</option>
              <option value="yes">Existing debt: Yes</option>
            </select>
            <select
              className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
              value={form.existing_investors ? "yes" : "no"}
              onChange={(e) => setForm({ ...form, existing_investors: e.target.value === "yes" })}
            >
              <option value="no">Existing investors: No</option>
              <option value="yes">Existing investors: Yes</option>
            </select>
            <select
              className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
              value={form.revenue_stage}
              onChange={(e) => setForm({ ...form, revenue_stage: e.target.value })}
            >
              <option value="Pre-revenue">Pre-revenue</option>
              <option value="Early">Early</option>
              <option value="Stable">Stable</option>
            </select>
            <input
              className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950 md:col-span-2"
              placeholder="Intended use of funds (comma separated)"
              value={form.intended_use_of_funds.join(\", \")}
              onChange={(e) =>
                setForm({ ...form, intended_use_of_funds: e.target.value.split(\",\").map((item) => item.trim()).filter(Boolean) })
              }
            />
            <select
              className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
              value={form.target_funding_size}
              onChange={(e) => setForm({ ...form, target_funding_size: e.target.value })}
            >
              <option value="$250k-$1M">$250k-$1M</option>
              <option value="$1M-$5M">$1M-$5M</option>
              <option value="$5M+">$5M+</option>
            </select>
            <select
              className="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm dark:border-slate-800 dark:bg-slate-950"
              value={form.preferred_timeline}
              onChange={(e) => setForm({ ...form, preferred_timeline: e.target.value })}
            >
              <option value="0-3 months">0-3 months</option>
              <option value="3-6 months">3-6 months</option>
              <option value="6+ months">6+ months</option>
            </select>
          </div>
          <Button className="mt-6" onClick={createStartup}>
            Save startup profile
          </Button>
        </Card>
      )}

      <div className="grid gap-4">
        {startups.map((startup) => (
          <Card key={startup.startup_code} className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-lg font-semibold">{startup.name}</div>
                <div className="text-sm text-slate-500 dark:text-slate-400">
                  {startup.industry} · {startup.country}
                </div>
              </div>
              <StatusPill
                status={
                  startup.status === "application_pending"
                    ? "pending"
                    : startup.status === "live"
                    ? "published"
                    : startup.status
                }
                label={
                  startup.status === "application_pending"
                    ? "Application Pending"
                    : startup.status === "live"
                    ? "Live"
                    : startup.status === "approved"
                    ? "Approved"
                    : "Draft"
                }
              />
            </div>
            <div className="mt-4 grid gap-2 text-sm text-slate-500 dark:text-slate-400 md:grid-cols-3">
              <div>Total raised ${(startup.total_raised_cents / 100).toLocaleString()}</div>
              <div>Active round: {startup.active_round ? "Yes" : "No"}</div>
              <div>Last revenue: {startup.last_revenue_reported ?? "—"}</div>
            </div>
            <Button className="mt-4" onClick={() => navigate(`/app/founder/startups/${startup.id}`)}>
              Open Startup
            </Button>
          </Card>
        ))}
      </div>
    </div>
  );
}
