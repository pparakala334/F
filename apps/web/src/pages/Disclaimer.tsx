import { Card } from "../components/Card";

export default function Disclaimer() {
  return (
    <Card className="p-8">
      <h2 className="text-2xl font-semibold">Disclaimer</h2>
      <p className="mt-4 text-sm text-slate-300">
        This demo is for educational and illustrative purposes only. It does not constitute legal,
        financial, tax, or investment advice. Any projections, yields, or payout examples are
        illustrative only and do not guarantee future performance.
      </p>
    </Card>
  );
}
