# Prapatti Online — Migration Prototype

This repository is a work-in-progress migration of [prapatti.com](https://www.prapatti.com) from its current PHP/shared-hosting setup to a modern static site on Cloudflare Pages.

## About the Original Site

Prapatti Online has been running since 1999. It is a Srivaishnava devotional archive maintained by Ayyampet Rajagopalan, containing hundreds of stotras (devotional hymns) in multiple Indian scripts — Tamil, Telugu, Devanagari, Kannada, Malayalam, Bengali, Grantha, and Roman transliteration. The site serves approximately 340 daily visitors, many in India.

The original site runs on PHP with Apache on A2 Hosting (shared hosting, Detroit). Every page is hand-edited HTML. There is no CMS.

## Why Migrate?

| | Current (A2 Hosting) | After (Cloudflare Pages) |
|---|---|---|
| TTFB | ~1.7s | <50ms |
| Page load | ~2.3s | <400ms |
| Monthly cost | ~$10–20 | $0 |
| Hosting model | PHP/Apache shared | Static + edge CDN |

Cloudflare's global edge network serves pages from the nearest datacenter — significantly faster for visitors in India.

## What This Repo Contains

```
prapatti-hugo/      Hugo static site (the new frontend)
workers/
  guestbook/        Cloudflare Worker + D1 (SQLite) for the guestbook form
  pdf-proxy/        Cloudflare Worker proxying PDFs from R2 storage
  visit-counter/    Cloudflare Worker + KV for homepage visitor count
scripts/            Data migration and build utility scripts
```

## Architecture

- **Hugo** generates the static site from JSON data files and Markdown content
- **Cloudflare Pages** hosts and deploys the site on every git push
- **Cloudflare R2** stores the PDF files (not committed to git)
- **Cloudflare D1** (SQLite) stores guestbook entries
- **Cloudflare KV** stores the visitor counter
- **Cloudflare Turnstile** provides spam protection on the guestbook form

## Serverless Workers

All dynamic functionality is handled by three Cloudflare Workers — lightweight serverless functions that run at the edge with no servers to manage.

### `workers/guestbook/` — Guestbook API

Handles public guestbook submissions and admin moderation backed by **Cloudflare D1** (serverless SQLite).

**Spam protection:**
- **Cloudflare Turnstile** — CAPTCHA-free bot challenge verified server-side before any entry is written
- **Honeypot field** — hidden form field; any submission that fills it is silently dropped
- **Keyword filter** — regex patterns block common spam phrases (URLs, "casino", "crypto", etc.)
- Spam submissions return `200 OK` silently so bots get no signal

---

### `workers/visit-counter/` — Visitor Counter

Increments and returns a global visitor count stored in **Cloudflare KV** (key-value store).

### `workers/pdf-proxy/` — File Proxy

Serves PDFs and audio files stored in **Cloudflare R2** (object storage). Acts as a controlled gateway so R2 is never exposed directly.

---

### Deploying Workers

Each worker is deployed independently using [Wrangler](https://developers.cloudflare.com/workers/wrangler/), Cloudflare's CLI:

```sh
cd workers/guestbook
wrangler deploy

cd workers/visit-counter
wrangler deploy

cd workers/pdf-proxy
wrangler deploy
```

Secrets are set via `wrangler secret put <KEY>` and are never stored in the repository.

## Status

This is still a work in progress. The live production site remains at [prapatti.com](https://www.prapatti.com). This prototype is being reviewed at [dev.prapatti.com](https://dev.prapatti.com) before any cutover.

The migration is being done as **seva** (voluntary service) — no cost to the site owner.

## Note on Content

The stotra PDFs and their content belong to prapatti.com and are not included in this repository. PDF files are served from Cloudflare R2 and excluded via `.gitignore`.
