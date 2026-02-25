import fs from "fs";
import path from "path";

interface OrcidWork {
  title: string;
  type: string;
  year: string;
  journal: string;
  doi: string | null;
}

export function getOrcidWorks(): OrcidWork[] {
  const filePath = path.join(process.cwd(), "orcid_works.json");
  if (!fs.existsSync(filePath)) return [];

  const raw = JSON.parse(fs.readFileSync(filePath, "utf-8"));
  const groups = raw.group || [];

  return groups.map((group: Record<string, unknown>) => {
    const summaries = (group["work-summary"] as Record<string, unknown>[]) || [];
    if (!summaries.length) return null;

    const work = summaries[0] as Record<string, unknown>;
    const titleObj = work.title as Record<string, unknown> | undefined;
    const titleInner = titleObj?.title as Record<string, string> | undefined;
    const title = titleInner?.value || "Untitled";

    const workType = (work.type as string) || "unknown";

    const pubDate = work["publication-date"] as Record<string, Record<string, string>> | null;
    const year = pubDate?.year?.value || "n/a";

    const journal = work["journal-title"] as Record<string, string> | null;
    const journalName = journal?.value || "";

    const extIds = (work["external-ids"] as Record<string, unknown[]>) || {};
    const idList = (extIds["external-id"] as Record<string, string>[]) || [];
    const doiEntry = idList.find((e) => e["external-id-type"] === "doi");
    const doi = doiEntry ? doiEntry["external-id-value"] : null;

    return { title, type: workType, year, journal: journalName, doi };
  }).filter(Boolean) as OrcidWork[];
}
