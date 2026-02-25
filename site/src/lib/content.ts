import fs from "fs";
import path from "path";
import matter from "gray-matter";
import { unified } from "unified";
import remarkParse from "remark-parse";
import remarkGfm from "remark-gfm";
import remarkRehype from "remark-rehype";
import rehypeRaw from "rehype-raw";
import rehypeStringify from "rehype-stringify";
import { BasePost } from "./types";

const CONTENT_DIR = path.join(process.cwd(), "content");

let postsCache: BasePost[] | null = null;

function getMarkdownFiles(dir: string): string[] {
  if (!fs.existsSync(dir)) return [];
  const files: string[] = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...getMarkdownFiles(fullPath));
    } else if (entry.name.endsWith(".md")) {
      files.push(fullPath);
    }
  }
  return files;
}

function parseFilename(filename: string): {
  year: string;
  month: string;
  slug: string;
  date: string;
} {
  // Jekyll convention: YYYY-MM-DD-slug.md
  const name = path.basename(filename, ".md");
  const match = name.match(/^(\d{4})-(\d{2})-(\d{2})-(.+)$/);
  if (match) {
    return {
      year: match[1],
      month: match[2],
      slug: match[4],
      date: `${match[1]}-${match[2]}-${match[3]}`,
    };
  }
  // Fallback for files without date prefix
  return { year: "2000", month: "01", slug: name, date: "2000-01-01" };
}

export async function renderMarkdown(raw: string): Promise<string> {
  // Treat content that is just "." or empty as empty
  const trimmed = raw.trim();
  if (!trimmed || trimmed === ".") return "";

  const result = await unified()
    .use(remarkParse)
    .use(remarkGfm)
    .use(remarkRehype, { allowDangerousHtml: true })
    .use(rehypeRaw)
    .use(rehypeStringify)
    .process(trimmed);

  return String(result);
}

export function getAllPosts(): BasePost[] {
  if (postsCache) return postsCache;

  const files = getMarkdownFiles(CONTENT_DIR);
  const posts: BasePost[] = [];

  for (const filePath of files) {
    const raw = fs.readFileSync(filePath, "utf-8");
    const { data, content } = matter(raw);
    const parsed = parseFilename(filePath);

    // Use date from front matter if available, otherwise from filename
    let dateStr = parsed.date;
    if (data.date) {
      const d =
        typeof data.date === "string" ? new Date(data.date) : data.date;
      if (!isNaN(d.getTime())) {
        dateStr = d.toISOString().slice(0, 10);
        parsed.year = dateStr.slice(0, 4);
        parsed.month = dateStr.slice(5, 7);
      }
    }

    const post: BasePost = {
      // Spread front matter first so explicit fields override
      ...data,
      slug: parsed.slug,
      year: parsed.year,
      month: parsed.month,
      title: data.title || "Untitled",
      date: dateStr,
      category: data.category || "",
      subcategory: data.subcategory || undefined,
      comments: data.comments,
      ordinal: data.ordinal,
      content,
      htmlContent: "",
      website: data.website || undefined,
    };

    posts.push(post);
  }

  postsCache = posts;
  return posts;
}

export function getPostsByCategory(category: string): BasePost[] {
  return getAllPosts().filter(
    (p) => p.category?.toLowerCase() === category.toLowerCase()
  );
}

export function getPostsBySubcategory(
  category: string,
  subcategory: string
): BasePost[] {
  return getAllPosts().filter(
    (p) =>
      p.category?.toLowerCase() === category.toLowerCase() &&
      p.subcategory === subcategory
  );
}

export function getPostBySlug(
  year: string,
  month: string,
  slug: string
): BasePost | undefined {
  return getAllPosts().find(
    (p) => p.year === year && p.month === month && p.slug === slug
  );
}

export function getAllPostSlugs(): {
  year: string;
  month: string;
  slug: string;
}[] {
  return getAllPosts().map((p) => ({
    year: p.year,
    month: p.month,
    slug: p.slug,
  }));
}

export function sortByOrdinal<T extends { ordinal?: number }>(
  posts: T[]
): T[] {
  return [...posts].sort((a, b) => (a.ordinal ?? 999) - (b.ordinal ?? 999));
}

export function truncateContent(html: string, wordCount: number): string {
  const text = html.replace(/<[^>]*>/g, "");
  const words = text.split(/\s+/).slice(0, wordCount);
  return words.join(" ") + (words.length >= wordCount ? "..." : "");
}
