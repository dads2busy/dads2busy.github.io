import { z } from "zod";

export const siteExtrasSchema = z.object({
  tagline: z.string(),
  description: z.string(),
  homepage_sections: z.array(z.string()),
  polymath_callout: z.object({
    wikipedia_def: z.string(),
    schroeder_def: z.string(),
  }),
});

export type SiteExtras = z.infer<typeof siteExtrasSchema>;
