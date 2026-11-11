# Global Career Radar

A static, mobile-friendly job dashboard with a scheduled Python collector. It fetches public vacancies from employer-owned Greenhouse and Lever applicant-tracking boards, filters for technology/architecture roles, and publishes a refreshed `data/jobs.json` every morning.

## Included
- Search and filters for Ghana vs international, remote/hybrid/onsite, relocation status, seniority and recent posts.
- Save jobs in the browser and export filtered results to CSV.
- Official application links only; no fabricated sample vacancies.
- GitHub Actions refresh at 05:00 UTC daily (05:00 Ghana time).
- Relocation is `Offered` only when the job description explicitly says so. Otherwise it is `Not stated`; explicit denials are `Not offered`.

## Deploy free with GitHub Pages
1. Create/sign in to a GitHub account at https://github.com.
2. Create a new **public** repository named `global-career-radar`.
3. Upload all files and folders in this project to the repository root (including the hidden `.github` folder).
4. In the repository, open **Settings → Pages**.
5. Under **Build and deployment**, choose **Deploy from a branch**, branch `main`, folder `/ (root)`, then Save.
6. Wait for GitHub Pages to publish. The site URL will be shown in Settings → Pages, usually `https://YOUR-USERNAME.github.io/global-career-radar/`.
7. Open **Actions** and run **Refresh verified job listings** once manually. The daily scheduled run then refreshes at 05:00 Ghana time.

## Important source coverage note
The collector currently reads employer-owned public Greenhouse and Lever boards listed in `sources.json`. It does not scrape LinkedIn or Jobberman pages and does not claim comprehensive market coverage. Add an employer's exact Greenhouse board token or Lever site slug to `sources.json` to extend coverage. Public board APIs may change or rate-limit; check the Actions log if a source fails.

## Add an employer source
- Greenhouse: add `{ "name": "Employer", "token": "exact-board-token" }` under `greenhouse`.
- Lever: add `{ "name": "Employer", "site": "exact-site-slug" }` under `lever`.

## Local preview
Run `python -m http.server 8000` from the project folder and open http://localhost:8000. The collector can be run with `python scripts/collect_jobs.py`.

## Verification limitations
A public ATS board is an authentic employer-controlled source, but the collector cannot independently guarantee that every vacancy remains open at the moment a user clicks. Always re-check the live employer application page. A missing relocation statement is deliberately not interpreted as relocation being unavailable.
