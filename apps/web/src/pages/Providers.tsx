import { useEffect, useState } from "react";
import { Button } from "../components/ui/button";
import { Card } from "../components/Card";
import { apiGet, apiPost } from "../lib/api";

interface Provider {
  provider_code: string;
  name: string;
  category: string;
  description: string;
}

export default function Providers() {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [form, setForm] = useState({ name: "", category: "", description: "" });

  useEffect(() => {
    apiGet<Provider[]>("/services").then(setProviders).catch(() => setProviders([]));
  }, []);

  const requestIntro = async () => {
    await apiPost("/services/intro", { provider_id: 1, requester_id: 2 });
    setMessage("Intro request sent (demo).");
  };

  const createProvider = async () => {
    await apiPost("/services", form);
    const next = await apiGet<Provider[]>("/services");
    setProviders(next);
    setForm({ name: "", category: "", description: "" });
    setMessage("Provider listing created (demo).");
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Service providers</h2>
      <Card className="p-6">
        <h3 className="text-lg font-semibold">Create a listing</h3>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          <input
            className="rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950 px-4 py-2 text-sm"
            placeholder="Provider name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />
          <input
            className="rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950 px-4 py-2 text-sm"
            placeholder="Category"
            value={form.category}
            onChange={(e) => setForm({ ...form, category: e.target.value })}
          />
          <input
            className="rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950 px-4 py-2 text-sm"
            placeholder="Description"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
        </div>
        <Button className="mt-4" onClick={createProvider}>Create listing</Button>
      </Card>
      <div className="grid gap-6 lg:grid-cols-2">
        {providers.map((provider) => (
          <Card key={provider.provider_code} className="p-6">
            <div className="text-sm uppercase text-slate-500">{provider.category}</div>
            <h3 className="mt-2 text-lg font-semibold">{provider.name}</h3>
            <p className="mt-2 text-sm text-slate-400">{provider.description}</p>
            <Button className="mt-4" onClick={requestIntro}>Request intro</Button>
          </Card>
        ))}
      </div>
      {message && <div className="text-sm text-slate-500 dark:text-slate-400">{message}</div>}
    </div>
  );
}
