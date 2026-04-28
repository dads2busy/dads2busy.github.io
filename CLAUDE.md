# CLAUDE.md — dads2busy.github.io

Personal academic portfolio website for **Aaron D. Schroeder, Ph.D.**  
URL: https://dads2busy.github.io

---

## Tech Stack

- **Next.js 16** (App Router, TypeScript, static export)
- **Tailwind CSS v4** (`@import "tailwindcss"`, `@theme inline` for token overrides)
- **Fonts**: Google Fonts via `next/font/google`
- **Content**: Markdown files with YAML front matter in `site/content/`, parsed at build time with `gray-matter`
- **Deployment**: GitHub Actions → GitHub Pages (`site/out/` static output)

```
site/
  src/
    app/           # Next.js App Router pages
    components/    # Shared React components
    lib/           # constants.ts, types.ts, content.ts
  content/         # 260+ markdown posts across 20+ categories
  public/          # Static assets (images, PDFs)
  out/             # Built static output (gitignored in site/)
orcid_works.py     # Fetches publications from ORCID API
```

## Development

```bash
cd site
npm run dev      # http://localhost:3000
npm run build    # Builds to site/out/
```

Pushes to `master` auto-deploy via `.github/workflows/deploy.yml`.

---

## Design System (Redesign — April 2026)

A visual + content redesign was started. The goal: modernize from dated Bootstrap 2.x style
to a warm scholarly palette with editorial typography.

### Design Tokens (defined in `globals.css` `:root`)

| Token              | Value     | Use |
|--------------------|-----------|-----|
| `--bg`             | `#f7f5f0` | Page background (warm off-white) |
| `--surface`        | `#f9f8f4` | Card/panel backgrounds |
| `--surface-offset` | `#edeae3` | Inset/callout backgrounds |
| `--border`         | `#dbd8d0` | All borders |
| `--text`           | `#1d1a14` | Primary text |
| `--text-muted`     | `#6a6760` | Secondary text |
| `--text-faint`     | `#aaa8a3` | Tertiary/decorative text |
| `--accent`         | `#14233a` | Deep navy — headings, links, primary |
| `--accent-light`   | `#e8edf5` | Chip backgrounds |
| `--gold`           | `#b8720a` | Warm gold — section labels, highlights |
| `--gold-light`     | `#fdf0d4` | Gold chip hover |
| `--nav-bg`         | `#0f1c2e` | Navbar + footer background |
| `--nav-text`       | `#c4c1b8` | Nav link text |
| `--nav-active`     | `#e8c87a` | Active nav item + site name |

### Typography

- **Display font**: `Instrument Serif` (Google Fonts) — `--font-instrument-serif` → `--font-display`
  - Used for: `h1` on home page, navbar site name, footer site name
  - Minimum size: 24px (`--text-xl`)
- **Body font**: `Inter` (Google Fonts) — `--font-inter` → `--font-body`
  - All body text, buttons, nav items, labels
- **Mono font**: `Geist Mono` — `--font-geist-mono` → `--font-code`

### CSS Utility Classes (in `globals.css`)

- `.section-label` — gold uppercase tracking label above sections
- `.panel` — surface card with border + shadow
- `.chip` — small inline skill/tag badge (navy, hover → gold)
- `.well` — legacy Bootstrap-style panel (kept for category pages)
- `.biosketch` — bio paragraph with 1.75 line-height

---

## Redesign Status (April 2026)

### ✅ Completed
- `site/src/app/globals.css` — full rewrite with new design tokens, component classes

### ⏳ Pending — code ready, not yet written to disk

All four files below have been fully designed/written; apply them when ready:

#### `site/src/app/layout.tsx`
Key changes:
- Replace `Geist` + `Geist_Mono` imports with `Inter`, `Instrument_Serif`, `Geist_Mono`
- Font variables: `--font-inter`, `--font-instrument-serif`, `--font-geist-mono`
- Remove `pb-12` from body className (footer is no longer fixed)
- Change `max-w-7xl` → `max-w-5xl` on `<main>`
- Update metadata title separator from ` - ` to ` — `

#### `site/src/components/Navbar.tsx`
Key changes:
- Use `var(--nav-*)` CSS tokens for all colors (drop Tailwind `neutral-*` classes)
- Site name uses `var(--font-display)` + `var(--nav-active)` color
- Tighter font sizing on nav items (0.8125rem)
- Hover handled via `onMouseEnter/Leave` with CSS variable colors

#### `site/src/components/Footer.tsx`
Key changes:
- **Remove** `fixed bottom-0 left-0 right-0 z-50` — make it a normal page footer
- Add affiliation info (name, title, division, email)
- Add two-column nav link grid from `NAV_ITEMS`
- Add CC BY 4.0 license link
- Use `var(--nav-*)` tokens for dark background

#### `site/src/app/page.tsx`
Key changes (full redesign):
- **Remove** sidebar/well Bootstrap layout
- **Hero section**: photo (left) + name/title/tagline (right) flex layout
- **Research Focus**: `.panel` card with bolded project names
- **2-column grid**: Education (left) | Specializations + `.chip` skill tags (right)
- **Honors table**: `.panel` with `divide-y`, year shown in gold on the right
- **Polymath callout**: left-bordered box with 2-col Wikipedia vs. Aaron definition
- Skills array: `R, Python, PostgreSQL, Oracle PL/SQL, MS SQL Server, Linux Admin, Docker, JavaEE, ASP.NET/C#, SAS, SPSS, Network Admin, Photoshop/GIMP, LLMs/AI`

---

## Content Structure

| Nav Label       | Route          | Content source |
|-----------------|----------------|----------------|
| Writing         | `/writing`     | `content/writing/` — academic publications, grouped by subcategory |
| Teaching        | `/teaching`    | `content/teaching/` |
| Working         | `/working`     | `content/working/` |
| Researching     | `/research`    | `content/research/` |
| Speaking        | `/speaking`    | `content/speaking/` |
| Coaching        | `/coaching`    | `content/coaching/` |
| Playing         | `/guitar`      | `content/guitar/` |
| Data Scienceing | `/datascience` | Multiple DS subcategories |
| Githubing       | (external)     | https://github.com/dads2busy |

All category pages use `CategoryLayout` → `Sidebar` → `LinksList` component pattern.  
Sidebar shows site tagline + contextual links for the current category.

## Key Constants (`site/src/lib/constants.ts`)

- `SITE_NAME` = `"Aaron Schroeder"`
- `SITE_TITLE` = `"Libération de Données!"`
- `SITE_DESCRIPTION` = the full polymath tagline
- `SITE_URL` = `"https://dads2busy.github.io"`
- `GITHUB_USERNAME` = `"dads2busy"`

## ORCID Integration

`orcid_works.py` (at repo root) does two things:

1. **Fetches** publications from the ORCID Public API using credentials in `.env`:
   ```
   ORCID_CLIENT_ID=APP-...
   ORCID_CLIENT_SECRET=...
   ORCID_ID=0000-0003-4372-2241   # or pass on CLI
   ```
   Output: `orcid_works.json` (committed snapshot of the last sync).

2. **Diffs** the fetched works against `site/content/profile.yaml` (the SSOT) and writes `orcid_diff.md` (gitignored) with three sections:
   - **Already in profile.yaml** — entries the SSOT and ORCID agree on
   - **Candidate NEW entries** — ORCID entries not yet in the SSOT, with ready-to-paste YAML
   - **Fuzzy matches** — DOI matches but title differs (stale SSOT metadata to review)

   Run: `.venv/bin/python orcid_works.py`

   Review `orcid_diff.md` and hand-paste accepted entries into `site/content/profile.yaml`. The script never edits `profile.yaml` directly.

Pure functions are in `scripts/orcid_diff_lib.py` with pytest coverage (`scripts/tests/test_orcid_diff_lib.py`).
