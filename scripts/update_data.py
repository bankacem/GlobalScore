#!/usr/bin/env python3
"""Refresh the static GlobalScore data snapshot.

The script intentionally stores only match metadata and RSS headlines/links.
It does not copy full third-party articles into the repository.
"""
from __future__ import annotations

import html
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "assets" / "data" / "content.json"
LIVE_FILE = ROOT / "assets" / "data" / "live.json"
API_BASE = "https://www.thesportsdb.com/api/v1/json/123"
LEAGUES = {
    4328: ("Premier League", "الدوري الإنجليزي الممتاز"),
    4335: ("La Liga", "الدوري الإسباني"),
    4829: ("Egyptian Premier League", "الدوري المصري الممتاز"),
}
RSS_URL = "https://feeds.bbci.co.uk/sport/football/rss.xml"
PLAYER_TERMS = {
    "player", "players", "transfer", "injury", "captain", "goalkeeper", "striker",
    "salah", "saka", "odegaard", "mbappe", "haaland", "vinicius", "bellingham",
    "messi", "ronaldo", "kane", "de bruyne", "palmer", "lewandowski", "yamal",
}


def fetch_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "GlobalScore/1.0 (+https://bankacem.github.io/GlobalScore/)"})
    with urlopen(request, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "GlobalScore/1.0 (+https://bankacem.github.io/GlobalScore/)"})
    with urlopen(request, timeout=25) as response:
        return response.read().decode("utf-8", errors="replace")


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def event_to_match(event: dict, league_en: str, league_ar: str, now: datetime) -> dict:
    status_raw = (event.get("strStatus") or "").lower()
    progress = event.get("strProgress") or ""
    timestamp = event.get("strTimestamp") or ""
    try:
        start = datetime.fromisoformat(timestamp.replace("Z", "+00:00")).replace(tzinfo=timezone.utc)
    except ValueError:
        start = now
    if any(token in status_raw for token in ("finished", "ft", "cancelled", "postponed")):
        status = "FT" if "cancel" not in status_raw and "postpon" not in status_raw else "Scheduled"
    elif progress or (start <= now <= start + timedelta(hours=2)):
        status = "Live"
    else:
        status = "Scheduled"
    home_score = event.get("intHomeScore")
    away_score = event.get("intAwayScore")
    score = f"{home_score or 0} - {away_score or 0}"
    local_start = start.astimezone()
    time_value = local_start.strftime("%H:%M") if timestamp else "--:--"
    return {
        "id": event.get("idEvent"),
        "date": start.date().isoformat(),
        "league": league_en,
        "leagueAr": league_ar,
        "home": event.get("strHomeTeam") or "Home",
        "homeAr": event.get("strHomeTeam") or "Home",
        "away": event.get("strAwayTeam") or "Away",
        "awayAr": event.get("strAwayTeam") or "Away",
        "homeLogo": event.get("strHomeTeamBadge") or "⚽",
        "awayLogo": event.get("strAwayTeamBadge") or "⚽",
        "score": score,
        "status": status,
        "minute": 0,
        "time": time_value,
        "day": local_start.strftime("%d"),
        "month": local_start.strftime("%b").upper(),
        "dayAr": local_start.strftime("%d"),
        "monthAr": local_start.strftime("%m/%Y"),
        "lineups": None,
        "stats": [],
        "events": [],
        "source": "TheSportsDB",
    }


def fetch_fixtures(now: datetime, fallback: list) -> list:
    collected: list[dict] = []
    seen: set[str] = set()
    for league_id, (league_en, league_ar) in LEAGUES.items():
        for endpoint in ("eventsday.php", "eventsnextleague.php"):
            params = {"d": now.strftime("%Y-%m-%d"), "l": league_id} if endpoint == "eventsday.php" else {"id": league_id}
            try:
                payload = fetch_json(f"{API_BASE}/{endpoint}?{urlencode(params)}")
            except Exception as exc:
                print(f"warning: {endpoint} for {league_en}: {exc}")
                continue
            events = payload.get("events") or []
            for event in events:
                event_id = str(event.get("idEvent") or "")
                if event_id and event_id not in seen and event.get("strSport") == "Soccer":
                    seen.add(event_id)
                    collected.append(event_to_match(event, league_en, league_ar, now))
    return collected[:24] or fallback


def fetch_player_news(fallback: list) -> list:
    previous = list(fallback)
    manual_fallback = [article for article in fallback if not article.get("external")]
    try:
        root = ElementTree.fromstring(fetch_text(RSS_URL))
    except Exception as exc:
        print(f"warning: RSS fetch failed: {exc}")
        return previous or manual_fallback
    stories: list[dict] = []
    for item in root.findall(".//item"):
        title = clean_text(item.findtext("title"))
        link = clean_text(item.findtext("link"))
        description = clean_text(item.findtext("description"))
        pub_date = clean_text(item.findtext("pubDate"))
        haystack = f"{title} {description}".lower()
        if not title or not link or not any(term in haystack for term in PLAYER_TERMS):
            continue
        stories.append({
            "slug": "external-player-news",
            "category": "Player news",
            "categoryAr": "أخبار اللاعبين",
            "title": title,
            "titleAr": title,
            "excerpt": (description[:180] + "…") if len(description) > 180 else description,
            "excerptAr": "عنوان ومقتطف من مصدر BBC Sport؛ افتح الرابط لقراءة التقرير الأصلي.",
            "date": pub_date or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "dateAr": pub_date or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "readTime": "Source link",
            "readTimeAr": "رابط المصدر",
            "href": link,
            "external": True,
            "source": "BBC Sport",
        })
        if len(stories) == 3:
            break
    return stories + manual_fallback if stories else (previous or manual_fallback)


def update_sitemaps(lastmod: str) -> None:
    date_value = lastmod[:10]
    for filename in ("Sitemap.xml", "sitemap.xml", "sitemap-index.xml"):
        path = ROOT / filename
        if path.exists():
            value = path.read_text(encoding="utf-8")
            value = re.sub(r"<lastmod>[^<]+</lastmod>", f"<lastmod>{date_value}</lastmod>", value)
            path.write_text(value, encoding="utf-8")


def main() -> None:
    existing = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    live_data = json.loads(LIVE_FILE.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc)
    existing["fixtures"] = fetch_fixtures(now, existing.get("fixtures") or live_data.get("matches", []))
    live_data["matches"] = existing["fixtures"]
    existing["articles"] = fetch_player_news(existing.get("articles", []))
    existing["lastUpdated"] = now.isoformat().replace("+00:00", "Z")
    DATA_FILE.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    live_data["updatedAt"] = existing["lastUpdated"]
    LIVE_FILE.write_text(json.dumps(live_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    update_sitemaps(existing["lastUpdated"])
    print(f"updated {len(existing['fixtures'])} fixtures, {len(existing['articles'])} stories, and live.json at {existing['lastUpdated']}")


if __name__ == "__main__":
    main()
