import { NavItem } from "./types";

export const SITE_NAME = "Aaron Schroeder";
export const SITE_TITLE = "Libération de Données!";
export const SITE_DESCRIPTION =
  "The entirely too-many activities of Aaron David Schroeder -- Epistemologist, Methodologist, Technologist, Musicologist, Research Scientist, Coach[ologist], Dad[ologist], Husband (amateur), Fisherman (rank amateur)";
export const SITE_URL = "https://dads2busy.github.io";
export const GITHUB_USERNAME = "dads2busy";

export const NAV_ITEMS: NavItem[] = [
  { label: "Writing", href: "/writing" },
  { label: "Researching", href: "/research" },
  { label: "Releasing", href: "/releases" },
  { label: "Speaking", href: "/speaking" },
  { label: "Teaching", href: "/teaching" },
  { label: "Working", href: "/working" },
  { label: "Playing", href: "/guitar" },
  { label: "Data Scienceing", href: "/datascience" },
  {
    label: "Githubing",
    href: `https://github.com/${GITHUB_USERNAME}`,
    external: true,
  },
];

export const DS_CATEGORIES = [
  "dataprofiling",
  "datadiscovery",
  "datalinkage",
  "datapreparation",
  "dataexploration",
  "datafitness",
  "datamanagement",
  "datascience",
  "r",
  "MANN",
  "serverconfig",
  "tools",
  "workstationconfig",
];

export const RESEARCH_SUBCATEGORIES = [
  "Data Integration & Management",
  "Program Evaluation/Policy Analysis",
  "Policy Implementation Networks",
  "Web-Enabled Public Services",
  "Wireless Technologies",
  "Activity Measurement",
];
