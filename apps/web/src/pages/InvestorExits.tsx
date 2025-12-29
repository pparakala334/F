import { useState } from "react";
import { Card } from "../components/Card";
import { Button } from "../components/ui/button";
import { ConfirmModal } from "../components/ConfirmModal";
import { apiPost } from "../lib/api";

export default function InvestorExits() {
  const [contractCode, setContractCode] = useState("CTR-0001");
  const [type, setType] = useState("quarterly");
  const [modalOpen, setModalOpen] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const submit = async () => {
    const id = Number(contractCode.split("-")[1]);
    await apiPost("/investor/exits/request", { contract_id: id, exit_type: type });
    setMessage("Exit request submitted.");
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Exit requests</h2>
      <Card className="p-6">
        <div className="grid gap-3 md:grid-cols-3">
          <input
            className="rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950 px-4 py-2 text-sm"
            value={contractCode}
            onChange={(e) => setContractCode(e.target.value)}
          />
          <select
            className="rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950 px-4 py-2 text-sm"
            value={type}
            onChange={(e) => setType(e.target.value)}
          >
            <option value="quarterly">Quarterly window</option>
            <option value="offcycle">Off-cycle</option>
          </select>
          <Button onClick={() => setModalOpen(true)}>Request exit</Button>
        </div>
        {message && <div className="mt-3 text-sm text-slate-500 dark:text-slate-400">{message}</div>}
      </Card>
      <ConfirmModal
        open={modalOpen}
        onOpenChange={setModalOpen}
        title="Exit confirmation"
        description="Exit requests are subject to minimum holding periods and applicable fees."
        confirmLabel="Confirm exit"
        onConfirm={submit}
      />
    </div>
  );
}
