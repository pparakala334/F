import { z } from "zod";

export const roundSchema = z.object({
  roundCode: z.string(),
  startupName: z.string(),
  status: z.string(),
});

export type RoundSummary = z.infer<typeof roundSchema>;
