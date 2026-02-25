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
  content: string;
  htmlContent: string;
  website?: string;
}

export interface ResearchPost extends BasePost {
  sponsor?: string;
  award?: string;
  dates?: string;
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
  sponsor?: string;
  authors?: string;
  editors?: string;
  pages?: string;
  DOI?: string;
  dates?: string;
}

export interface SpeakingPost extends BasePost {
  sponsor?: string;
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
