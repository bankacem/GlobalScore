# GlobalScore

GlobalScore is a static, mobile-first football hub for live-score presentation, upcoming fixtures, league tables, original match reports, tactical notes, and player-watch stories. It is designed for GitHub Pages and now includes a free scheduled data-refresh workflow.

## What changed

The interface now has a clear editorial hierarchy: a branded hero, a daily match board, upcoming fixtures, original stories, a league sidebar, favourites, dark mode, multilingual navigation, and accessible focus/skip-link states. Arabic and English homepages use matching canonical and `hreflang` metadata, while every article has its own canonical URL and structured Article metadata.

The content layer is stored as a JSON snapshot. `assets/data/live.json` contains the scoreboard and standings, while `assets/data/content.json` contains fixture cards and editorial stories. The previous five-second random live-score simulator was removed so the site does not present fabricated changes as real-time data.

## Free automatic data refresh

`.github/workflows/update-sports-data.yml` runs manually or daily at 05:17 UTC as a durable fallback snapshot. In the browser, `assets/js/data-source.js` polls the public ESPN scoreboard JSON endpoints every 15 seconds for Premier League, La Liga, and UEFA Champions League matches. It falls back to the latest generated JSON when ESPN has no response. The workflow calls `scripts/update_data.py`, which fetches fixture metadata from TheSportsDB's documented free v1 API and reads football headlines from the BBC Sport RSS feed. It stores match metadata and short source-linked headlines only; it does not copy full third-party articles. The workflow commits the refreshed JSON and updates sitemap dates, after which GitHub Pages publishes the new snapshot.

No API key is required for the documented TheSportsDB free v1 key. The workflow uses the repository's built-in GitHub token only to commit the generated snapshot. Because scheduled workflows run from the repository's default branch, the workflow is pinned to the current GitHub Pages branch. GitHub may disable scheduled workflows after long periods without repository activity, so the workflow also supports `workflow_dispatch` for a manual refresh.

The ESPN scoreboard endpoint used by the live browser view currently responds with CORS enabled and a short cache window, but it is a public endpoint rather than a contractual API product. It may change or rate-limit traffic without notice; if that happens, the generated snapshot remains available. If a future provider requires a secret key, place it in GitHub Actions Secrets and read it from the workflow environment; never put it in HTML or client-side JavaScript.

## Sitemap and Search Console

The repository now includes both `Sitemap.xml` and `sitemap.xml` for compatibility with the URL previously submitted to Search Console. The root sitemap lists the four language homepages, editorial pages, permanent match centers, team pages, and competition hubs using absolute URLs. `robots.txt` references both spellings, and `sitemap-index.xml` points to the canonical root sitemap.

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

## Live standings and team comparison

The dashboard now fetches standings from ESPN's public v2 soccer standings endpoint for the Premier League, La Liga, and UEFA Champions League. It displays rank, team badge, matches played, wins, draws, losses, goals for, goals against, goal difference, points, and form, with the local JSON tables retained as a fallback. The league view refreshes every ten minutes while the live scoreboard continues refreshing every 15 seconds.

Match details also turn the available ESPN box-score statistics into a side-by-side comparison with proportional bars for the home and away teams. No paid API key is required. Because these are public endpoints rather than an official commercial integration, availability and field coverage may change.

## Daily multilingual article automation

`.github/workflows/update-sports-data.yml` now runs every day at 05:17 UTC and remains manually runnable through `workflow_dispatch`. It refreshes the free TheSportsDB snapshot and BBC Sport RSS headlines, then runs `scripts/generate_multilingual_articles.py`. The generator selects up to ten unfinished matches for today and tomorrow from ESPN; when ESPN rejects automated requests, it uses the refreshed local TheSportsDB snapshot instead. It never fabricates a fixture when a real scheduled fixture is available.

For every selected match, the generator writes an original preview in Arabic, English, French, and Spanish, adds `canonical`, four `hreflang` links, Open Graph metadata, and `Article` JSON-LD, then updates both sitemap spellings. `assets/data/article_registry.json` records the event identifier, stable date-based slug, teams, date, generation time, and languages. The registry and event key prevent the same match from creating duplicate records on repeated workflow runs; an existing page is updated rather than duplicated.

The workflow commits the generated HTML, JSON snapshot, registry, and sitemap to the GitHub Pages branch using the built-in GitHub token. No paid translation API, AI API key, or external database is required. The multilingual copy is generated from original language-specific editorial templates, which keeps the process deterministic and free. If a source is unavailable, the workflow preserves the last usable snapshot and continues without deleting the existing editorial pages.

## Permanent match, team and competition pages

The generator `scripts/generate_permanent_pages.py` creates crawlable pages under `/matches/`, `/teams/`, and `/leagues/` for Arabic, English, French, and Spanish. A permanent match center server-renders the fixture, score snapshot, competition, date, time, and SportsEvent JSON-LD, then enriches events, referee, venue, attendance, line-ups, and statistics in the browser from the public ESPN summary endpoint when available. The free local snapshot remains the fallback and no secret key is exposed to the browser.

Articles and fixture cards link to the relevant match center, both team pages, and the competition hub using descriptive anchor text. Team pages collect their fixtures and related previews; competition pages collect fixtures and the available fallback standings. These pages are generated from verified snapshot data only, so unavailable live fields are shown as unavailable instead of being invented. The service worker cache is versioned when the permanent-page assets change.

## Editorial SEO standard

The article generator uses a people-first structure rather than a fixed keyword or word-count formula. Each new preview has a descriptive title and meta description, a factual match card, a clear tactical angle, observable questions, a confirmation boundary, contextual internal links, and a small number of relevant external sources. The pages use crawlable anchor elements, canonical URLs, four language alternates plus `x-default`, Open Graph metadata, and `Article` JSON-LD with author, publisher, publication and modification dates.

The editorial target is to remain concise and useful, normally below 1,400 words; this is a project quality limit, not a Google ranking requirement. Google does not guarantee first-page placement from word count, keywords, schema, or a sitemap alone. Sustainable visibility depends on original analysis, factual accuracy, a clear site focus, trustworthy sourcing, technical accessibility, links earned from relevant sites, and evidence that readers find the page satisfying. The generator therefore avoids invented line-ups, injuries, statistics, and events, preserves old URLs, and does not change historical sitemap dates merely to make pages appear fresh.

The player-analysis example `player-watch-odegaard.html` is available in Arabic, English, French, and Spanish. It demonstrates the same standard with a concrete tactical thesis, questions a reader can verify from the match, three internal GlobalScore links, official Arsenal and Premier League reference links, and a transparent editorial note.

## Search and player discovery

The repository now generates `/search/`, `/players/`, and `/players/martin-odegaard.html` for Arabic, English, French, and Spanish through `scripts/generate_discovery_pages.py`. The search page indexes the local fixture snapshot, team and competition pages, internal editorial articles, and source-linked BBC Sport headlines in the browser. Pressing Enter in the homepage search field opens the full search route with the query preserved.

The player area separates original GlobalScore analysis from external source-linked headlines. The Martin Ødegaard profile uses official Arsenal and Premier League reference links and does not invent current injuries, line-ups, or statistics. External headlines open on their source website, while internal analysis remains on GlobalScore. The daily Actions workflow regenerates these discovery pages after the data, article, and permanent match pages.

## Player performance dashboard

Player profiles now include a free client-side performance dashboard. `assets/js/player-performance.js` reads the public ESPN athlete profile endpoint when it is available and renders the season summary returned by the source: starts and substitute appearances, goals, assists, and shots. The dashboard uses responsive KPI cards, a horizontal bar chart, and a relative radar profile; the radar is explicitly a relative visualization and not a proprietary player rating.

The profile identifies the season and links to the ESPN source. Missing values are shown as unavailable rather than estimated, and the page remains useful through its original editorial analysis and official reference links. The endpoint is public and may rate-limit or change without notice, so the dashboard is intentionally non-blocking and does not expose credentials. The daily workflow includes the performance asset in its commit list, while `sw.js` is versioned when the dashboard changes.
