import { motion } from "framer-motion";
import { Button } from "../components/ui/button";
import { Card } from "../components/Card";
import { InfoModal } from "../components/InfoModal";
import { useEffect, useMemo, useState } from "react";

export default function Landing() {
  const [legalOpen, setLegalOpen] = useState(false);
  const sections = useMemo(
    () => [
      { id: "product", label: "Product" },
      { id: "how", label: "How it works" },
      { id: "pricing", label: "Pricing" },
      { id: "safety", label: "Safety" },
      { id: "faq", label: "FAQ" },
    ],
    []
  );
  const [active, setActive] = useState("product");

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (visible?.target?.id) {
          setActive(visible.target.id);
        }
      },
      { rootMargin: "-30% 0px -40% 0px", threshold: [0.2, 0.4, 0.6, 0.8] }
    );

    sections.forEach((section) => {
      const el = document.getElementById(section.id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, [sections]);

  return (
    <div className="relative space-y-20">
      <div className="pointer-events-auto fixed right-6 top-1/3 z-40 hidden flex-col gap-3 text-right md:flex">
        {sections.map((section) => (
          <a
            key={section.id}
            href={`#${section.id}`}
            className={`transition-all ${
              active === section.id
                ? "text-lg font-semibold text-slate-900 dark:text-white"
                : "text-xs text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200"
            }`}
          >
            {section.label}
          </a>
        ))}
      </div>
      <section id="product" className="grid gap-8 lg:grid-cols-2 items-center">
        <div className="space-y-6">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-4xl font-semibold"
          >
            Revenue-share funding that keeps founders in control and investors aligned.
          </motion.h1>
          <p className="text-slate-600 dark:text-slate-300">
            Launch revenue-share rounds with deterministic tiers, transparent caps, and automated reporting.
            Offer a clear path to exits without diluting ownership.
          </p>
          <div className="flex gap-4">
            <Button>Request access</Button>
            <Button variant="outline">View live marketplace</Button>
          </div>
        </div>
        <Card className="p-6 glass">
          <div className="space-y-4">
            <div className="text-sm uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Marketplace snapshot
            </div>
            <div className="text-2xl font-semibold">$28.4M committed capital</div>
            <div className="text-sm text-slate-500 dark:text-slate-400">
              Illustrative projections only. No guaranteed returns.
            </div>
            <div className="grid grid-cols-3 gap-3 text-center text-xs">
              <div className="rounded-2xl bg-white/70 p-4 dark:bg-slate-900/60">
                <div className="text-lg font-semibold">32</div>
                <div className="text-slate-500 dark:text-slate-400">Active rounds</div>
              </div>
              <div className="rounded-2xl bg-white/70 p-4 dark:bg-slate-900/60">
                <div className="text-lg font-semibold">5.1%</div>
                <div className="text-slate-500 dark:text-slate-400">Median share</div>
              </div>
              <div className="rounded-2xl bg-white/70 p-4 dark:bg-slate-900/60">
                <div className="text-lg font-semibold">1.6x</div>
                <div className="text-slate-500 dark:text-slate-400">Median cap</div>
              </div>
            </div>
          </div>
        </Card>
      </section>

      <section id="how" className="grid gap-6 lg:grid-cols-3">
        {[
          {
            title: "Apply and get approved",
            body: "Founders submit a streamlined application and financial documents. Admins review and approve in one workflow.",
          },
          {
            title: "Select a tier, publish the round",
            body: "Our deterministic algorithm proposes low/medium/high tiers with clear explanations and caps.",
          },
          {
            title: "Report revenue, distribute payouts",
            body: "Monthly revenue reports trigger investor distributions with full auditability and ledger entries.",
          },
        ].map((section) => (
          <motion.div
            key={section.title}
            whileInView={{ opacity: 1, y: 0 }}
            initial={{ opacity: 0, y: 20 }}
            transition={{ duration: 0.4 }}
            viewport={{ once: true }}
          >
            <Card className="p-6">
              <h3 className="text-lg font-semibold">{section.title}</h3>
              <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">{section.body}</p>
            </Card>
          </motion.div>
        ))}
      </section>

      <section id="pricing" className="rounded-3xl border border-slate-200 bg-gradient-to-r from-amber-200/30 to-transparent p-10 dark:border-slate-800 dark:from-amber-500/10">
        <div className="grid gap-6 lg:grid-cols-2">
          <div>
            <h2 className="text-2xl font-semibold">Transparent pricing</h2>
            <p className="mt-3 text-sm text-slate-600 dark:text-slate-300">
              Application fees, platform processing fees, and optional loan referral fees are disclosed before you publish.
            </p>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="outline">Download fee schedule</Button>
          </div>
        </div>
      </section>

      <section id="safety" className="grid min-h-[320px] gap-6 lg:grid-cols-2">
        <Card className="p-6">
          <h3 className="text-lg font-semibold">Canada-first compliance controls</h3>
          <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
            Country-mode enforcement, identity verification, and audit trails keep the marketplace compliant.
          </p>
        </Card>
        <Card className="p-6">
          <h3 className="text-lg font-semibold">Operational transparency</h3>
          <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
            Investors receive reporting, payout history, and exit options with defined fees and holding periods.
          </p>
        </Card>
      </section>

      <section id="faq" className="grid min-h-[320px] gap-6 lg:grid-cols-2">
        <Card className="p-6">
          <h3 className="text-lg font-semibold">Is this equity?</h3>
          <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
            No. Investors receive a capped revenue share until a payout cap or time cap is reached.
          </p>
        </Card>
        <Card className="p-6">
          <h3 className="text-lg font-semibold">How are payouts calculated?</h3>
          <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
            Payouts are a fixed percentage of reported gross revenue and tracked in the platform ledger.
          </p>
        </Card>
      </section>

      <footer className="border-t border-slate-800 pt-8 text-sm text-slate-500">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <span>© 2024 Steelman. All rights reserved.</span>
          <button onClick={() => setLegalOpen(true)} className="text-slate-400 hover:text-white">
            Legal & Disclosures
          </button>
        </div>
      </footer>

      <InfoModal
        open={legalOpen}
        onOpenChange={setLegalOpen}
        title="Legal & Disclosures"
        description="This platform provides illustrative projections only and does not constitute legal, financial, or investment advice."
      />
    </div>
  );
}
