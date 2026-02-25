/**
 * One-time migration script: converts speaking/ and writing/ markdown files
 * into speaking.json and writing.json in the content directory.
 *
 * Usage: node scripts/migrate-to-json.mjs
 */

import fs from "fs";
import path from "path";
import matter from "gray-matter";

const CONTENT_DIR = path.join(process.cwd(), "content");

function parseFilename(filename) {
  const name = path.basename(filename, ".md");
  const match = name.match(/^(\d{4})-(\d{2})-(\d{2})-(.+)$/);
  if (match) {
    return { year: match[1], month: match[2], day: match[3], slug: match[4] };
  }
  return { year: "2000", month: "01", day: "01", slug: name };
}

function migrateCategory(category, fieldsToKeep) {
  const dir = path.join(CONTENT_DIR, category);
  if (!fs.existsSync(dir)) {
    console.log(`No directory found for ${category}, skipping.`);
    return;
  }

  const files = fs.readdirSync(dir).filter((f) => f.endsWith(".md")).sort();
  const entries = [];

  for (const file of files) {
    const raw = fs.readFileSync(path.join(dir, file), "utf-8");
    const { data, content } = matter(raw);
    const parsed = parseFilename(file);

    // Resolve date: prefer frontmatter, fall back to filename
    let dateStr = `${parsed.year}-${parsed.month}-${parsed.day}`;
    if (data.date) {
      const d = typeof data.date === "string" ? new Date(data.date) : data.date;
      if (!isNaN(d.getTime())) {
        dateStr = d.toISOString().slice(0, 10);
      }
    }

    const entry = { slug: parsed.slug, date: dateStr };

    // Copy specified fields from frontmatter
    for (const field of fieldsToKeep) {
      if (data[field] !== undefined && data[field] !== null) {
        entry[field] = data[field];
      } else {
        entry[field] = "";
      }
    }

    // Store the raw markdown body
    entry.content = content.trim();

    entries.push(entry);
  }

  // Sort by date descending (newest first)
  entries.sort((a, b) => b.date.localeCompare(a.date));

  const outPath = path.join(CONTENT_DIR, `${category}.json`);
  fs.writeFileSync(outPath, JSON.stringify(entries, null, 2) + "\n");
  console.log(`Wrote ${entries.length} entries to ${outPath}`);
}

// Speaking fields (excluding layout, category, award, comments)
migrateCategory("speaking", [
  "title",
  "subcategory",
  "sponsor",
  "dates",
  "role",
  "website",
  "report",
  "media1",
  "media2",
  "media3",
  "media1title",
  "media2title",
  "media3title",
]);

// Writing fields (excluding layout, category, comments)
migrateCategory("writing", [
  "title",
  "subcategory",
  "sponsor",
  "dates",
  "authors",
  "editors",
  "pages",
  "DOI",
  "website",
  "ordinal",
]);
