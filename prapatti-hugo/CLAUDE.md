# Prapatti Online — Hugo site

Hugo static site for [prapatti.com](https://www.prapatti.com), a Srivaishnava stotras archive (since 1999), moving from PHP on A2 Hosting to Cloudflare. It is live for review at https://dev.prapatti.com; prapatti.com still runs on A2 until the switchover.

The owner, Ayyampet Rajagopalan, is non-technical. Keep every workflow as simple as possible; this is a seva project, not a product.

## How it is put together

- **Pages:** Hugo templates in `layouts/`, built from JSON in `data/`. Pushing to `main` on GitHub rebuilds dev.prapatti.com (Cloudflare Pages).
- **PDFs and MP3s:** not in git. They live in the R2 bucket `prapatti-files` under `slokas/<script>/...` and are served by the `prapatti-pdf-proxy` worker. Script folders: english (Roman), sanskrit (Devanagari), kannada, bengali, malayalam, telugu, tamil, grantha, mp3.
- **Workers** (in `../workers/`): `guestbook` (D1; new entries wait for approval at /forum/admin), `visit-counter` (KV), `pdf-proxy` (R2).

## Data files

| File | Shown on |
|------|----------|
| `data/stotras_index.json` | All Stotras page and both search boxes |
| `data/updates.json` | Latest Updates on the home page and /updates/<year>/ |
| `data/categories/<slug>.json` + `content/categories/<slug>.md` | Pages for multi-part works (folder icon), e.g. Bhaagavatam skandhas |
| `data/major_works.json` | Major Works cards on the home page |
| `data/special_event.json` | Event banner on the home page (`active: true/false`) |
| `data/articles.json`, `data/announcements.json` | Resources page |

## Adding a stotra (the current workflow, Cloudflare only)

1. Upload PDFs: `rclone copy <folder> r2:prapatti-files/slokas --include "*.pdf" --include "*.mp3"`
2. `python3 scripts/add-stotra.py <file-name> --name "..." --author "..." [--update "..."]` — adds it to `stotras_index.json` (and `updates.json` with `--update`), finding the scripts present in R2.
3. Push.

The A2 sync scripts (`convert-categories.py`, `convert-updates.py`, `build-stotras-from-php.py`, `fix-pdf-links.py`) rebuild data from prapatti.com's PHP. `build-stotras-from-php.py` rebuilds the whole stotra list, so it drops stotras added with `add-stotra.py`; do not run it once stotras are added directly.

## Search

`static/js/stotra-search.js` is shared by the home page and /stotras/. It matches every query word in any order and folds transliteration variants (aa/a, ee/i, sh/s, w/v, x/ks, doubled letters, spaces), with a prefix fallback for long words.

## Commands

```bash
hugo server            # preview at http://localhost:1313
cd ../workers/<name> && wrangler deploy
```
