import * as Dialog from "@radix-ui/react-dialog";
import { Button } from "./ui/button";

interface InfoModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description: string;
}

export function InfoModal({ open, onOpenChange, title, description }: InfoModalProps) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-charcoal/40 dark:bg-black/70" />
        <Dialog.Content className="fixed left-1/2 top-1/2 w-[90%] max-w-lg -translate-x-1/2 -translate-y-1/2 rounded-3xl border border-slate-200 bg-cream p-6 text-slate-900 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-100">
          <Dialog.Title className="text-lg font-semibold">{title}</Dialog.Title>
          <Dialog.Description className="mt-3 text-sm text-slate-400">{description}</Dialog.Description>
          <div className="mt-6 flex justify-end">
            <Button onClick={() => onOpenChange(false)}>Close</Button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
