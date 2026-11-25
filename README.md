# Purpose-Driven Careers Radar

A public, lightweight job discovery radar focused on remote opportunities accessible to professionals based in Brazil, with additional LATAM and worldwide opportunities.

## MVP scope

Five initial categories:

1. HR & Talent Acquisition
2. Learning & Development
3. Non-profit, Social Impact & Sustainability
4. Customer Experience & Operations
5. Project & Business Operations

The first version uses public job-board APIs, Python classification, JSON storage, GitHub Actions for daily collection, and GitHub Pages for the public interface.

## Important eligibility rule

A job is included only when its location/eligibility text explicitly indicates Brazil, Latin America/LATAM, or worldwide/global/anywhere eligibility. A generic "Remote" label is **not** enough. This reduces false positives, but automated text checks are not a guarantee: always verify the original posting before applying.

## Set up the public repository

1. Create a **public** GitHub repository named `purpose-driven-careers-radar`.
2. Download and unzip this starter project.
3. Upload all files and folders to the repository's root (keep `.github/workflows/`).
4. In GitHub, open **Settings → Pages** and set the build source to **GitHub Actions**.
5. Open **Actions** and enable workflows if GitHub asks.
6. Run **Daily job radar update** manually once from the Actions tab.
7. When the deployment workflow finishes, your site will be available at:
   `https://YOUR-GITHUB-USERNAME.github.io/purpose-driven-careers-radar/`

## Local preview

Requires Python 3.10+.

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`.

To collect jobs locally:

```bash
python scripts/collect_jobs.py
```

The collector uses only public endpoints and Python's standard library. No API key is required for the initial sources.

## Sources in the MVP

- Remotive public remote-jobs API
- Arbeitnow public jobs API

The MVP intentionally starts with two sources. Add career sites and nonprofit/impact job boards only after their access method, terms, and location fields have been checked. Do not scrape sites that prohibit it.

## Schedule

GitHub Actions is scheduled for 10:00 UTC (07:00 in Curitiba/Brasília, UTC−3). GitHub may delay scheduled workflows during periods of high load; the time is not guaranteed to be exact.

## Data fields

Each job includes title, company, category, location eligibility, source, original URL, date found, date posted (when available), employment type (when available), and a short description.

## Roadmap

- [ ] Add curated organization career pages (including animal welfare and environmental organizations)
- [ ] Add more nonprofit and international-development job boards
- [ ] Improve eligibility evidence and manual review workflow
- [ ] Add salary and contract-type filters when reliable data is available
- [ ] Add saved searches or email digests (optional)
- [ ] Add tests and monitoring for broken sources

## Responsible use

This project links to original job postings and does not claim affiliation with employers or job boards. Check each employer's current hiring location, work authorization, time-zone, language, and contract requirements before applying.
