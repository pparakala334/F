import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Card } from "../components/Card";
import { Skeleton } from "../components/Skeleton";
import { StatusPill } from "../components/StatusPill";
import { apiGet } from "../lib/api";

interface RoundSummary {
  round_code: string;
  startup_name: string;
  status: string;
  max_raise_cents: number;
  selected_tier: string;
}

export default function Discover() {
  const [rounds, setRounds] = useState<RoundSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet<RoundSummary[]>("/rounds/published")
      .then(setRounds)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Discover rounds</h2>
        <p className="text-sm text-slate-400">
          Browse published revenue-share rounds. Projections are illustrative only.
        </p>
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        {loading && Array.from({ length: 2 }).map((_, index) => <Skeleton key={index} className="h-48" />)}
        {!loading &&
          rounds.map((round) => (
            <Card key={round.round_code} className="p-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">{round.startup_name}</h3>
                <StatusPill status={round.status} />
              </div>
              <p className="mt-2 text-sm text-slate-400">Round {round.round_code}</p>
              <div className="mt-4 flex items-center justify-between text-sm text-slate-300">
                <div>Max raise: ${(round.max_raise_cents / 100).toLocaleString()}</div>
                <div>Tier: {round.selected_tier}</div>
              </div>
              <Link
                className="mt-6 inline-flex text-sm text-slate-600 hover:text-slate-800 dark:text-slate-300 dark:hover:text-slate-100"
                to={`/rounds/${round.round_code}`}
              >
                View details
              </Link>
            </Card>
          ))}
      </div>
    </div>
  );
}
