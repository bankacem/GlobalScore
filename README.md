# GlobalScore

GlobalScore is a static, mobile-first football hub for live-score presentation, upcoming fixtures, league tables, original match reports, tactical notes, and player-watch stories. It is designed for GitHub Pages and now includes a free scheduled data-refresh workflow.

## What changed

The interface now has a clear editorial hierarchy: a branded hero, a daily match board, upcoming fixtures, original stories, a league sidebar, favourites, dark mode, multilingual navigation, and accessible focus/skip-link states. Arabic and English homepages use matching canonical and `hreflang` metadata, while every article has its own canonical URL and structured Article metadata.

The content layer is stored as a JSON snapshot. `assets/data/live.json` contains the scoreboard and standings, while `assets/data/content.json` contains fixture cards and editorial stories. The previous five-second random live-score simulator was removed so the site does not present fabricated changes as real-time data.

## Free automatic data refresh

`.github/workflows/update-sports-data.yml` runs manually or every six hours as a durable fallback snapshot. In the browser, `assets/js/data-source.js` polls the public ESPN scoreboard JSON endpoints every 15 seconds for Premier League, La Liga, and UEFA Champions League matches. It falls back to the latest generated JSON when ESPN has no response. The workflow calls `scripts/update_data.py`, which fetches fixture metadata from TheSportsDB's documented free v1 API and reads football headlines from the BBC Sport RSS feed. It stores match metadata and short source-linked headlines only; it does not copy full third-party articles. The workflow commits the refreshed JSON and updates sitemap dates, after which GitHub Pages publishes the new snapshot.

No API key is required for the documented TheSportsDB free v1 key. The workflow uses the repository's built-in GitHub token only to commit the generated snapshot. Because scheduled workflows run from the repository's default branch, the workflow is pinned to the current GitHub Pages branch. GitHub may disable scheduled workflows after long periods without repository activity, so the workflow also supports `workflow_dispatch` for a manual refresh.

The ESPN scoreboard endpoint used by the live browser view currently responds with CORS enabled and a short cache window, but it is a public endpoint rather than a contractual API product. It may change or rate-limit traffic without notice; if that happens, the generated snapshot remains available. If a future provider requires a secret key, place it in GitHub Actions Secrets and read it from the workflow environment; never put it in HTML or client-side JavaScript.

## Sitemap and Search Console

The repository now includes both `Sitemap.xml` and `sitemap.xml` for compatibility with the URL previously submitted to Search Console. The root sitemap lists the English and Arabic homepages plus all six article pages using absolute URLs. `robots.txt` references both spellings, and `sitemap-index.xml` points to the canonical root sitemap.

Submit this exact URL in Google Search Console:

```text
https://bankacem.github.io/GlobalScore/Sitemap.xml
```

After GitHub Pages publishes the commit, open the URL in a browser and confirm that it returns XML rather than an HTML 404 page. Google recommends absolute canonical URLs, UTF-8 XML, and a sitemap at the site root; a sitemap improves discovery but does not guarantee indexing.

## Local development

Because the site uses JavaScript modules, serve it through a local HTTP server:

```bash
python3 -m http.server 4173
```

Then open `http://localhost:4173/en/` or `http://localhost:4173/ar/`.

## Project structure

```text
/en/ and /ar/                 multilingual homepages
/en/articles/ and /ar/articles/  indexable editorial pages
  /assets/data/live.json         generated fallback scores and standings
  /assets/data/content.json      refreshed fixtures and editorial content snapshot
/scripts/update_data.py          free API/RSS fetch and sanitisation
/.github/workflows/              scheduled data refresh
/assets/js/                    data loading, rendering, favourites and theme logic
  /assets/css/                   critical and full responsive styling
  /assets/js/data-source.js      ESPN live polling plus JSON fallback
Sitemap.xml                    root sitemap requested by Search Console
sitemap.xml                    lowercase compatibility copy
sitemap-index.xml              sitemap index
robots.txt                     crawler directives
```

## Editorial workflow

To publish a new article, add the Arabic and English HTML pages under their respective `articles/` directories, add a bilingual entry to `assets/data/content.json`, and add both canonical URLs to `Sitemap.xml` and `sitemap.xml`. Keep the title, description, publication date, canonical URL, and `hreflang` links consistent.
