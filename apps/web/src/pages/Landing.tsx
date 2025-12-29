import { motion } from "framer-motion";
import { Button } from "../components/ui/button";
import { Card } from "../components/Card";

const sections = [
  {
    title: "Revenue-share funding, aligned with founder outcomes",
    body: "Offer investors a capped revenue share instead of equity dilution. Keep control while building long-term partners.",
  },
  {
    title: "Investor-first transparency",
    body: "Monthly revenue reporting, automated payout tracking, and clear exit windows with transparent fees.",
  },
  {
    title: "Operational support",
    body: "Access vetted service providers, data-driven tiers, and a compliant, Canada-first marketplace configuration.",
  },
];

export default function Landing() {
  return (
    <div className="space-y-16">
      <section className="grid gap-8 lg:grid-cols-2 items-center">
        <div className="space-y-6">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-4xl font-semibold"
          >
            Build a revenue-share funding round that respects founders and investors.
          </motion.h1>
          <p className="text-slate-300">
            Launch funding rounds with deterministic tiers, automate monthly distributions, and offer
            optional loan referrals. No equity. No hype. Just aligned outcomes.
          </p>
          <div className="flex gap-4">
            <Button>Start a demo round</Button>
            <Button variant="outline">View investor portal</Button>
          </div>
        </div>
        <Card className="p-6 glass">
          <div className="space-y-4">
            <div className="text-sm uppercase tracking-wide text-slate-400">Marketplace snapshot</div>
            <div className="text-2xl font-semibold">$2.8M published rounds</div>
            <div className="text-sm text-slate-400">Illustrative projections only. No guaranteed returns.</div>
            <div className="grid grid-cols-3 gap-3 text-center text-xs">
              <div className="rounded-2xl bg-slate-900/60 p-4">
                <div className="text-lg font-semibold">18</div>
                <div className="text-slate-400">Active rounds</div>
              </div>
              <div className="rounded-2xl bg-slate-900/60 p-4">
                <div className="text-lg font-semibold">4.6%</div>
                <div className="text-slate-400">Median share</div>
              </div>
              <div className="rounded-2xl bg-slate-900/60 p-4">
                <div className="text-lg font-semibold">1.5x</div>
                <div className="text-slate-400">Median cap</div>
              </div>
            </div>
          </div>
        </Card>
      </section>

      <section className="grid gap-6 lg:grid-cols-3">
        {sections.map((section) => (
          <motion.div
            key={section.title}
            whileInView={{ opacity: 1, y: 0 }}
            initial={{ opacity: 0, y: 20 }}
            transition={{ duration: 0.4 }}
            viewport={{ once: true }}
          >
            <Card className="p-6">
              <h3 className="text-lg font-semibold">{section.title}</h3>
              <p className="mt-3 text-sm text-slate-400">{section.body}</p>
            </Card>
          </motion.div>
        ))}
      </section>

      <section className="rounded-3xl border border-slate-800 bg-gradient-to-r from-indigo-500/10 to-transparent p-10">
        <div className="grid gap-6 lg:grid-cols-2">
          <div>
            <h2 className="text-2xl font-semibold">Canada-first compliance controls</h2>
            <p className="mt-3 text-sm text-slate-300">
              Enforce Canada-only participation with configurable country modes and automated validations.
            </p>
          </div>
          <div className="flex items-center gap-4">
            <Button>View compliance mode</Button>
            <Button variant="ghost">Read disclaimer</Button>
          </div>
        </div>
      </section>
    </div>
  );
}
