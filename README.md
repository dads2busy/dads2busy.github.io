# dads2busy.github.io

Personal academic portfolio website for Aaron D. Schroeder, Ph.D. -- Research Associate Professor at the Social & Decision Analytics Division, University of Virginia Biocomplexity Institute.

## Tech Stack

- **Next.js 15** with App Router and TypeScript
- **Tailwind CSS** for styling
- **Static export** deployed to GitHub Pages via GitHub Actions
- Markdown content with YAML front matter, parsed at build time with `gray-matter`

## Structure

- `site/` -- Next.js project (source code, components, content)
- `site/content/` -- 261 markdown posts across 20+ categories
- `site/public/` -- static assets (images, downloadable PDFs)
- `old jekyll site/` -- archived original Jekyll site
- `orcid_works.py` -- script to fetch publications from ORCID API

## Development

```bash
cd site
npm install
npm run dev
```

Open http://localhost:3000

## Build

```bash
cd site
npm run build
```

Static output is generated in `site/out/`.

## Deployment

Pushes to `master` trigger the GitHub Actions workflow (`.github/workflows/deploy.yml`) which builds and deploys to GitHub Pages automatically.

## License

Content is licensed under [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/legalcode).
