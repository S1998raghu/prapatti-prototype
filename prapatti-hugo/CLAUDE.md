# Prapatti Online — Hugo Prototype

## What this project is

A Hugo static site prototype for [prapatti.com](https://www.prapatti.com), a Srivaishnava devotional stotras archive that has been running since 1999. The goal is to migrate the site from PHP on shared hosting (A2 Hosting, Detroit) to a static Hugo build deployed on Cloudflare Pages — making it faster, free to host, and easier to maintain.

The live site is currently at `prapatti.com`. This prototype will be deployed at `beta.prapatti.com` for the owner to review before any migration.

## Owner context

- **Name:** Ayyampet Rajagopalan
- **Location:** Mason, Ohio, USA
- **Age:** 55+
- **Technical level:** Manages the site himself — edits HTML directly, uploads via FTP, no CMS
- **Email:** contact@prapatti.com
- **Current hosting:** A2 Hosting (shared PHP/Apache), paid until December 2025
- **Domain registrar:** Aplus.net, paid until December 2031

**This matters for every decision:** The owner is non-technical. His workflow must stay as simple as possible. Any admin interface needs to be dead simple. Do not over-engineer.

## Current site architecture (what we're replacing)

- PHP with 3 includes: `header.html`, `categorycarousel.html`, `footer.html`
- The PHP does nothing else — the entire page is hardcoded HTML
- Updates table: manually written `<tr>` rows, ~125 entries extracted and stored in `data/updates.json`
- Special events: ~30+ commented-out Bootstrap alert banners, one shown at a time by uncommenting
- Stotras are served as **PDFs** — they live in `/slokas/{script}/filename.pdf` on the server
- Scripts supported: Roman (english), Kannada, Bengali, Malayalam, Devanagari (sanskrit), Telugu, Tamil, Grantha
- Audio files exist for some stotras (MP3s)
- JS stack being replaced: jQuery 3.3.1 + Bootstrap 4 + DataTables (all served from A2 Hosting)
- Guestbook: PHP form → MySQL on A2 Hosting. Moderated — owner approves each entry manually, sometimes replies inline

## Hugo project structure

```
prapatti-hugo/
├── CLAUDE.md              ← you are here
├── hugo.toml              ← site config, baseURL = https://beta.prapatti.com/
├── content/
│   ├── _index.md          ← homepage
│   ├── stotras/           ← stotra index and category pages
│   ├── guestbook/         ← guestbook page
│   ├── resources/         ← links and articles
│   └── donate/            ← UPI + Stripe donation page
├── data/
│   ├── updates.json       ← 125 update entries extracted from index.php (date, description, links per script)
│   ├── major_works.json   ← 8 major works shown on homepage
│   └── special_event.json ← currently active special event banner (active: true/false, title, url)
├── layouts/
│   ├── _default/
│   │   ├── baseof.html    ← base HTML shell (loads CSS, header, footer)
│   │   ├── single.html    ← default single page
│   │   └── list.html      ← default list page
│   ├── partials/
│   │   ├── header.html    ← topbar + sticky nav + search input
│   │   └── footer.html    ← footer with links and copyright
│   └── index.html         ← homepage layout (hero, event banner, works grid, updates table, guestbook strip, donate strip)
├── static/
│   ├── css/main.css       ← full design system (cream/gold/ink palette, all components)
│   ├── js/search.js       ← client-side search over updates (Fuse.js or plain JS)
│   └── slokas/            ← PDF files go here (mirror from A2 Hosting)
└── assets/                ← Hugo pipes assets (if needed)
```

## Design system

The design is a complete departure from the current Bootstrap 4 site. Key decisions:

- **Palette:** Cream (`#FDFAF4`), Ink (`#1C1410`), Gold (`#8B6914`) — warm, manuscript-like, devotional
- **Typography:** Crimson Pro (serif, for headings and shlokas) + DM Sans (sans, for UI)
- **No Bootstrap** — custom CSS only, much lighter
- **No jQuery** — vanilla JS only
- **Fonts loaded from Google Fonts** (Crimson Pro + DM Sans)
- Target audience: 60+ devotees on mobile, many in India — performance is critical

### Key components already built in `static/css/main.css`:
- Topbar (dark, multilingual invocation)
- Sticky nav bar with search
- Hero section with shloka and script selector
- Event banner (red, shown when `special_event.active = true`)
- Welcome strip
- Major works grid (4 columns, 2 on mobile)
- Updates table (replaces DataTables — clean, lightweight, styled)
- Guestbook strip (quote + CTA)
- Donate strip (UPI + Stripe buttons)
- Footer
- Full responsive breakpoints at 900px and 680px

## How to add a new stotra (owner's future workflow)

When Ayyampet adds a new stotra, he should only need to:

1. Add a new entry to `data/updates.json`:
```json
{
  "date": "Apr 17 2026",
  "description": "Stotra name and description here",
  "links": {
    "roman": "/slokas/english/filename.pdf",
    "tamil": "/slokas/tamil/filename.pdf",
    "telugu": "/slokas/telugu/filename.pdf"
  }
}
```
2. Upload the PDF files to `static/slokas/{script}/`
3. Run `hugo build` (or push to GitHub → auto-deploys via Cloudflare Pages)

## How to show/hide a special event

Edit `data/special_event.json`:
```json
{
  "active": true,
  "title": "Srii Ramanuja Jayanti, Chittirai Tiruvadirai",
  "url": "/splevents_Bhaashyakaarar.php"
}
```
Set `active: false` to hide it. This replaces the current workflow of manually commenting/uncommenting HTML.

## Guestbook plan

The guestbook is the only truly dynamic feature. Current plan:

- **User-facing:** Same as today — name, message, location fields → submit
- **Backend:** Cloudflare Worker + D1 database (SQLite, free tier)
- **Admin panel:** Simple password-protected page for Ayyampet to read entries and post replies
- **Migration:** Export existing MySQL entries from A2 Hosting before migration (years of community data)

Do NOT replace the guestbook with a third-party service — the owner reads and replies to every entry personally. That workflow must be preserved exactly.

## Donations plan

- **India visitors:** UPI QR code (static image) — PhonePe/GPay compatible, zero fees
- **International:** Stripe Payment Link (external redirect, no backend needed)
- Both live on `/donate/` page
- Framed as "seva" not "payment"

## Deployment plan

1. Build Hugo site locally
2. Push to GitHub repo (`prapatti-prototype`)
3. Connect to Cloudflare Pages (free tier, unlimited bandwidth)
4. Point `beta.prapatti.com` DNS to Cloudflare Pages (Ayyampet needs to add CNAME in Aplus.net)
5. Owner reviews at `beta.prapatti.com` alongside live `prapatti.com`
6. When approved: point `prapatti.com` to Cloudflare Pages, let A2 Hosting lapse in December

## What still needs to be built

- [ ] `static/js/search.js` — client-side search over `data/updates.json`
- [ ] `content/stotras/` — stotra index page (mirrors `stotras.php`)
- [ ] `content/stotras/by-category.md` — category listing (mirrors `stotrasbycategory.php`)
- [ ] `content/guestbook/` — guestbook page with form
- [ ] `content/resources/` — links and articles page
- [ ] `content/donate/` — UPI QR + Stripe button page
- [ ] `static/css/main.css` — finish responsive mobile styles (cut off mid-file)
- [ ] Cloudflare Worker for guestbook form submission
- [ ] GitHub Actions workflow for auto-deploy to Cloudflare Pages
- [ ] `netlify.toml` or `wrangler.toml` config for Cloudflare

## Key facts to know

| Item | Detail |
|------|--------|
| Live site performance | TTFB 1.7s, page load 2.3s, slower than 73% of web |
| After Cloudflare Pages | TTFB <50ms, load <400ms, Mumbai edge for India |
| Monthly hosting cost now | ~$10–20/month (A2 Hosting) |
| Monthly hosting cost after | $0 (Cloudflare Pages free tier) |
| Daily traffic | ~340 visitors, ~1,000 page views |
| Updates extracted | 125 entries from index.php into data/updates.json |
| Scripts supported | Roman, Kannada, Bengali, Malayalam, Devanagari, Telugu, Tamil, Grantha |
| Do NOT say | "PHP is outdated" — PHP is fine, the hosting model is the issue |

## Commands

```bash
# Local dev server
hugo server --buildDrafts

# Production build
hugo build

# New content page
hugo new content stotras/index.md
```

## Notes for Claude Code

- Always check `data/updates.json` before touching the updates table — all 125 entries are already there
- The CSS in `static/css/main.css` was cut off mid-file during generation — finish the responsive section
- Keep the design warm and devotional — resist the urge to modernise it into a generic tech site
- The owner is 55+, non-technical, primarily uses the site on desktop to manage it
- When in doubt, simpler is better — this is a seva project, not a product
