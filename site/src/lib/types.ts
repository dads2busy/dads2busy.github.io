export interface BasePost {
  slug: string;
  year: string;
  month: string;
  title: string;
  date: string;
  category: string;
  subcategory?: string;
  comments?: boolean;
  ordinal?: number;
  abstract: string;
  htmlContent: string;
  website?: string;
}

export interface ResearchPost extends BasePost {
  funder?: string;
  award?: string;
  dates?: string;
  start_year?: number;
  end_year?: number;
  role?: string;
  report?: string;
  report2?: string;
  report3?: string;
  report4?: string;
  report5?: string;
  report6?: string;
  media1?: string;
  media2?: string;
  media3?: string;
  media1title?: string;
  media2title?: string;
  media3title?: string;
}

export interface WritingPost extends BasePost {
  journal?: string;
  authors?: string;
  editors?: string;
  pages?: string;
  DOI?: string;
  dates?: string;
}

export interface SpeakingPost extends BasePost {
  event?: string;
  dates?: string;
  role?: string;
  report?: string;
  media1?: string;
  media2?: string;
  media3?: string;
  media1title?: string;
  media2title?: string;
  media3title?: string;
}

export interface WorkingPost extends BasePost {
  subtitle?: string;
  dates?: string;
}

export interface GuitarPost extends BasePost {
  artist?: string;
  file?: string;
}

export interface DataSciencePost extends BasePost {
  description?: string;
}

export interface NavItem {
  label: string;
  href: string;
  external?: boolean;
}
