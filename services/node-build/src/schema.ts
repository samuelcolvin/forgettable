import { z } from 'zod';

export const BuildRequestSchema = z.object({
  files: z
    .record(
      z.string().min(1), // file path
      z.string() // file content
    )
    .refine((files) => Object.keys(files).length > 0, {
      message: 'At least one file is required',
    }),
});

export type BuildRequest = z.infer<typeof BuildRequestSchema>;

export const BuildOutputSchema = z.record(z.string(), z.string());

export type BuildOutput = z.infer<typeof BuildOutputSchema>;
