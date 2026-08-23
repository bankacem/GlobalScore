from datetime import date
from html import escape
from pathlib import Path
import json
import re
import shutil
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://bankacem.github.io/GlobalScore'
LANGS = ('ar', 'en', 'fr', 'es')
LEAGUE_CODES = {
    'Premier League': 'eng.1',
    'الدوري الإنجليزي الممتاز': 'eng.1',
    'La Liga': 'esp.1',
    'الدوري الإسباني': 'esp.1',
    'UEFA Champions League': 'uefa.champions',
    'دوري أبطال أوروبا': 'uefa.champions',
    'Egyptian Premier League': 'egy.1',
    'الدوري المصري الممتاز': 'egy.1',
}
LEAGUE_OFFICIAL = {
    'eng.1': 'https://www.premierleague.com/en/',
    'esp.1': 'https://www.laliga.com/en-GB',
    'uefa.champions': 'https://www.uefa.com/uefachampionsleague/',
    'egy.1': 'https://www.espn.com/soccer/scoreboard/_/league/egy.1',
}
COPY = {
    'en': {
        'dir': 'ltr', 'home': 'GlobalScore home', 'articles': 'Match previews', 'live': 'Live scores', 'standings': 'Live standings',
        'match': 'Match center', 'teams': 'Teams', 'league': 'Competition', 'date': 'Date', 'time': 'Kick-off', 'status': 'Status',
        'venue': 'Venue', 'referee': 'Referee', 'attendance': 'Attendance', 'events': 'Match events', 'stats': 'Team comparison',
        'lineups': 'Players and line-ups', 'source': 'Data source', 'source_note': 'Initial fixture fields are server-rendered from the free snapshot. Live events, line-ups and statistics are enriched in the browser when the public ESPN feed is available.',
        'not_available': 'Not available yet', 'no_events': 'No published events yet.', 'no_stats': 'Statistics are not available yet.', 'no_lineups': 'Line-ups have not been announced yet.',
        'refresh': 'Auto-refresh when live data is available', 'open_map': 'Open venue on Google Maps', 'related': 'Related coverage', 'back': 'Back to GlobalScore',
        'upcoming': 'Fixtures and recent results', 'team_page': 'Team page', 'league_page': 'Competition page', 'view_details': 'Open match center', 'official': 'Official competition source',
        'last_update': 'Last checked', 'goals': 'Goals', 'cards': 'Cards', 'subs': 'Substitutions', 'table': 'Standings', 'matches': 'Matches', 'read': 'Read preview',
    },
    'ar': {
        'dir': 'rtl', 'home': 'العودة إلى GlobalScore', 'articles': 'معاينات المباريات', 'live': 'النتائج المباشرة', 'standings': 'الترتيب المباشر',
        'match': 'مركز المباراة', 'teams': 'الفرق', 'league': 'المسابقة', 'date': 'التاريخ', 'time': 'موعد البداية', 'status': 'الحالة',
        'venue': 'الملعب', 'referee': 'الحكم', 'attendance': 'الحضور', 'events': 'أحداث المباراة', 'stats': 'مقارنة الفريقين',
        'lineups': 'اللاعبون والتشكيلات', 'source': 'مصدر البيانات', 'source_note': 'تُعرض بيانات المباراة الأولية من snapshot المجاني على الخادم. وتُضاف الأحداث والتشكيلات والإحصائيات في المتصفح عند توفر موجز ESPN العام.',
        'not_available': 'غير متاح حالياً', 'no_events': 'لا توجد أحداث منشورة بعد.', 'no_stats': 'الإحصائيات غير متوفرة بعد.', 'no_lineups': 'لم يتم الإعلان عن التشكيلات بعد.',
        'refresh': 'تحديث تلقائي عند توفر البيانات الحية', 'open_map': 'فتح موقع الملعب على Google Maps', 'related': 'تغطية مرتبطة', 'back': 'العودة إلى GlobalScore',
        'upcoming': 'المباريات والنتائج الأخيرة', 'team_page': 'صفحة الفريق', 'league_page': 'صفحة المسابقة', 'view_details': 'فتح مركز المباراة', 'official': 'المصدر الرسمي للمسابقة',
        'last_update': 'آخر تحقق', 'goals': 'الأهداف', 'cards': 'البطاقات', 'subs': 'التبديلات', 'table': 'الترتيب', 'matches': 'المباريات', 'read': 'قراءة المعاينة',
    },
    'fr': {
        'dir': 'ltr', 'home': 'Retour à GlobalScore', 'articles': 'Avant-matchs', 'live': 'Scores en direct', 'standings': 'Classement en direct',
        'match': 'Centre du match', 'teams': 'Équipes', 'league': 'Compétition', 'date': 'Date', 'time': 'Coup d’envoi', 'status': 'Statut',
        'venue': 'Stade', 'referee': 'Arbitre', 'attendance': 'Affluence', 'events': 'Événements du match', 'stats': 'Comparaison des équipes',
        'lineups': 'Joueurs et compositions', 'source': 'Source des données', 'source_note': 'Les informations initiales sont rendues depuis le snapshot gratuit. Les événements, compositions et statistiques sont enrichis dans le navigateur lorsque le flux public ESPN est disponible.',
        'not_available': 'Pas encore disponible', 'no_events': 'Aucun événement publié pour le moment.', 'no_stats': 'Les statistiques ne sont pas encore disponibles.', 'no_lineups': 'Les compositions ne sont pas encore annoncées.',
        'refresh': 'Actualisation automatique si les données sont disponibles', 'open_map': 'Ouvrir le stade sur Google Maps', 'related': 'Couverture associée', 'back': 'Retour à GlobalScore',
        'upcoming': 'Matchs et résultats récents', 'team_page': 'Page de l’équipe', 'league_page': 'Page de la compétition', 'view_details': 'Ouvrir le centre du match', 'official': 'Source officielle de la compétition',
        'last_update': 'Dernière vérification', 'goals': 'Buts', 'cards': 'Cartons', 'subs': 'Remplacements', 'table': 'Classement', 'matches': 'Matchs', 'read': 'Lire l’avant-match',
    },
    'es': {
        'dir': 'ltr', 'home': 'Volver a GlobalScore', 'articles': 'Previas de partidos', 'live': 'Marcadores en directo', 'standings': 'Clasificación en directo',
        'match': 'Centro del partido', 'teams': 'Equipos', 'league': 'Competición', 'date': 'Fecha', 'time': 'Inicio', 'status': 'Estado',
        'venue': 'Estadio', 'referee': 'Árbitro', 'attendance': 'Asistencia', 'events': 'Acontecimientos del partido', 'stats': 'Comparación de equipos',
        'lineups': 'Jugadores y alineaciones', 'source': 'Fuente de datos', 'source_note': 'Los datos iniciales se generan desde el snapshot gratuito. Los acontecimientos, las alineaciones y las estadísticas se amplían en el navegador cuando está disponible el feed público de ESPN.',
        'not_available': 'Todavía no disponible', 'no_events': 'Todavía no hay acontecimientos publicados.', 'no_stats': 'Las estadísticas todavía no están disponibles.', 'no_lineups': 'Las alineaciones todavía no han sido anunciadas.',
        'refresh': 'Actualización automática cuando haya datos en directo', 'open_map': 'Abrir el estadio en Google Maps', 'related': 'Cobertura relacionada', 'back': 'Volver a GlobalScore',
        'upcoming': 'Partidos y resultados recientes', 'team_page': 'Página del equipo', 'league_page': 'Página de la competición', 'view_details': 'Abrir el centro del partido', 'official': 'Fuente oficial de la competición',
        'last_update': 'Última comprobación', 'goals': 'Goles', 'cards': 'Tarjetas', 'subs': 'Cambios', 'table': 'Clasificación', 'matches': 'Partidos', 'read': 'Leer la previa',
    },
}


def slugify(value):
    normalized = unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r'[^a-z0-9]+', '-', normalized).strip('-')


def load_data():
    content = json.loads((ROOT / 'assets/data/content.json').read_text(encoding='utf-8'))
    live = json.loads((ROOT / 'assets/data/live.json').read_text(encoding='utf-8'))
    live_by_id = {str(item.get('id')): item for item in live.get('matches', [])}
    fixtures = []
    for raw in content.get('fixtures', []):
        item = dict(live_by_id.get(str(raw.get('id')), {}))
        item.update(raw)
        league_name = item.get('league') or 'Premier League'
        code = LEAGUE_CODES.get(league_name, 'eng.1')
        item['leagueCode'] = code
        item['leagueEn'] = 'Premier League' if code == 'eng.1' else 'La Liga' if code == 'esp.1' else 'UEFA Champions League' if code == 'uefa.champions' else 'Egyptian Premier League'
        item['leagueAr'] = item.get('leagueAr') or ({'eng.1': 'الدوري الإنجليزي الممتاز', 'esp.1': 'الدوري الإسباني', 'uefa.champions': 'دوري أبطال أوروبا', 'egy.1': 'الدوري المصري الممتاز'}[code])
        item['home'] = item.get('home') or item.get('strHomeTeam') or 'Home'
        item['away'] = item.get('away') or item.get('strAwayTeam') or 'Away'
        item['id'] = str(item.get('id') or f'{item.get("date", "unknown")}-{slugify(item["home"])}-{slugify(item["away"])}')
        item['date'] = str(item.get('date') or date.today().isoformat())[:10]
        item['slug'] = f'{item["date"]}-{slugify(item["home"])}-{slugify(item["away"])}'
        fixtures.append(item)
    return fixtures, live.get('tables', {}), live.get('updatedAt', '')


def lang_name(item, lang):
    if lang == 'ar':
        return item.get('homeAr') or item.get('home')
    return item.get('home')


def esc(value):
    return escape(str(value or ''))


def shell(lang, title, description, canonical, hreflang, body, script=''):
    c = COPY[lang]
    canonical_path = canonical.split(f'{BASE}/{lang}/', 1)[1]
    default_href = f'{BASE}/en/{canonical_path}'
    return f'''<!doctype html><html lang="{lang}" dir="{c['dir']}" prefix="og: https://ogp.me/ns#"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} | GlobalScore</title><meta name="description" content="{esc(description)}"><meta name="robots" content="index,follow"><link rel="canonical" href="{canonical}">{hreflang}<link rel="alternate" hreflang="x-default" href="{default_href}"><link rel="stylesheet" href="../../assets/css/critical.css?v=4"><link rel="stylesheet" href="../../assets/css/main.css?v=10"><meta property="og:type" content="article"><meta property="og:site_name" content="GlobalScore"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{canonical}"><meta name="twitter:card" content="summary"><script type="application/ld+json">__SCHEMA__</script></head><body>{body}{script}</body></html>'''


def hreflang_for(path):
    return '\n'.join(f'<link rel="alternate" hreflang="{lang}" href="{BASE}/{lang}/{path}">' for lang in LANGS)


def nav(lang, active='match'):
    c = COPY[lang]
    return f'''<header class="site-header"><div class="header-container"><a class="brand" href="../"><img class="logo-img" src="../../assets/img/logo.svg" alt=""><span>Global<span class="brand-accent">Score</span></span></a><nav class="nav"><a class="nav-link" href="../">{esc(c['home'])}</a><a class="nav-link" href="../articles/">{esc(c['articles'])}</a><a class="nav-link" href="../#leagues">{esc(c['standings'])}</a></nav><div class="controls"><a class="language-btn" href="../../ar/">AR</a><a class="language-btn" href="../../en/">EN</a><a class="language-btn" href="../../fr/">FR</a><a class="language-btn" href="../../es/">ES</a></div></div></header>'''


def team_block(item, side, lang):
    name = item.get(side) or side.title()
    logo = item.get(f'{side}Logo') or ''
    logo_markup = f'<img src="{esc(logo)}" alt="" loading="lazy">' if str(logo).startswith('http') else '<span class="match-crest-fallback">⚽</span>'
    return f'<a class="match-team-panel" href="../teams/{slugify(name)}.html" title="{esc(name)}"><span class="match-crest">{logo_markup}</span><strong>{esc(name)}</strong></a>'


def match_page(item, lang):
    c = COPY[lang]
    match_path = f'matches/{item["id"]}.html'
    canonical = f'{BASE}/{lang}/{match_path}'
    home = item.get('home') or 'Home'
    away = item.get('away') or 'Away'
    league_en = item.get('leagueEn', item.get('league', 'Premier League'))
    league_label = item.get('leagueAr') if lang == 'ar' else league_en
    status = item.get('status') or 'Scheduled'
    status_label = {'Scheduled': {'ar': 'مجدولة', 'en': 'Scheduled', 'fr': 'Programmé', 'es': 'Programado'}, 'Live': {'ar': 'مباشر', 'en': 'Live', 'fr': 'En direct', 'es': 'En directo'}, 'FT': {'ar': 'انتهت', 'en': 'FT', 'fr': 'Terminé', 'es': 'Finalizado'}}.get(status, {}).get(lang, status)
    score = item.get('score') or '0 - 0'
    title = {'ar': f'مركز مباراة {home} و{away}: النتيجة والأحداث والتشكيلات', 'en': f'{home} vs {away} match center: score, events and line-ups', 'fr': f'{home} - {away} : centre du match, score et compositions', 'es': f'{home} - {away}: centro del partido, resultado y alineaciones'}[lang]
    description = {'ar': f'صفحة دائمة لمباراة {home} و{away} في {league_label}: النتيجة، الأحداث، التشكيلات والإحصائيات عند توفرها.', 'en': f'Permanent match center for {home} vs {away} in {league_label}: score, events, line-ups and statistics when available.', 'fr': f'Centre permanent de {home} - {away} en {league_label} : score, événements, compositions et statistiques disponibles.', 'es': f'Centro permanente de {home} - {away} en {league_label}: resultado, acontecimientos, alineaciones y estadísticas disponibles.'}[lang]
    facts = f'<div class="permanent-fact-grid"><div><small>{esc(c["league"])}</small><strong>{esc(league_label)}</strong></div><div><small>{esc(c["date"])}</small><strong>{esc(item.get("date"))}</strong></div><div><small>{esc(c["time"])}</small><strong>{esc(item.get("time") or "--:--")}</strong></div><div><small>{esc(c["source"])}</small><strong>ESPN / TheSportsDB</strong></div></div>'
    body = f'''{nav(lang)}<main class="page-shell permanent-page"><a class="article-back" href="../">← {esc(c['home'])}</a><section class="permanent-hero"><div class="permanent-kicker">{esc(c['match'])} · {esc(league_label)}</div><h1>{esc(title)}</h1><p>{esc(description)}</p><div class="match-scoreboard" data-match-id="{esc(item['id'])}">{team_block(item, 'home', lang)}<div class="match-score-column"><strong id="match-score">{esc(score)}</strong><span id="match-status">{esc(status_label)}</span><small id="match-minute">{esc(item.get('minute') or '')}</small></div>{team_block(item, 'away', lang)}</div></section>{facts}<section class="permanent-meta-grid"><div class="permanent-meta-card"><span>⚖️</span><small>{esc(c['referee'])}</small><strong id="match-referee">{esc(c['not_available'])}</strong></div><div class="permanent-meta-card"><span>🏟️</span><small>{esc(c['venue'])}</small><strong id="match-venue">{esc(c['not_available'])}</strong><a id="match-map" class="is-hidden" target="_blank" rel="noopener noreferrer">{esc(c['open_map'])}</a></div><div class="permanent-meta-card"><span>👥</span><small>{esc(c['attendance'])}</small><strong id="match-attendance">—</strong></div></section><section class="permanent-section"><div class="section-heading"><div><span class="section-kicker">{esc(c['events'])}</span><h2>{esc(c['events'])}</h2></div></div><div id="match-events" class="permanent-empty">{esc(c['no_events'])}</div></section><section class="permanent-section"><div class="section-heading"><div><span class="section-kicker">{esc(c['stats'])}</span><h2>{esc(c['stats'])}</h2></div></div><div id="match-stats" class="permanent-empty">{esc(c['no_stats'])}</div></section><section class="permanent-section"><div class="section-heading"><div><span class="section-kicker">{esc(c['lineups'])}</span><h2>{esc(c['lineups'])}</h2></div></div><div id="match-lineups" class="permanent-empty">{esc(c['no_lineups'])}</div></section><section class="permanent-section related-section"><div class="section-heading"><div><span class="section-kicker">{esc(c['related'])}</span><h2>{esc(c['related'])}</h2></div></div><div class="permanent-link-grid"><a href="../teams/{slugify(home)}.html">{esc(c['team_page'])}: {esc(home)}</a><a href="../teams/{slugify(away)}.html">{esc(c['team_page'])}: {esc(away)}</a><a href="../leagues/{slugify(league_en)}.html">{esc(c['league_page'])}: {esc(league_label)}</a><a href="../articles/{item['slug']}.html">{esc(c['articles'])}</a></div></section><p class="permanent-source-note">{esc(c['source_note'])}</p></main><footer class="footer"><div class="footer-inner"><a class="brand footer-brand" href="../"><img class="logo-img" src="../../assets/img/logo.svg" alt=""><span>Global<span class="brand-accent">Score</span></span></a><p>GlobalScore Editorial</p><a href="{esc(LEAGUE_OFFICIAL.get(item['leagueCode'], LEAGUE_OFFICIAL['eng.1']))}" target="_blank" rel="noopener noreferrer">{esc(c['official'])}</a></div></footer>'''
    schema = json.dumps({'@context': 'https://schema.org', '@type': 'SportsEvent', 'name': f'{home} vs {away}', 'description': description, 'url': canonical, 'startDate': f'{item["date"]}T{str(item.get("time") or "00:00")[:5]}:00Z', 'eventStatus': 'https://schema.org/EventScheduled' if status == 'Scheduled' else 'https://schema.org/EventInProgress', 'homeTeam': {'@type': 'SportsTeam', 'name': home}, 'awayTeam': {'@type': 'SportsTeam', 'name': away}, 'organizer': {'@type': 'SportsOrganization', 'name': league_en, 'url': LEAGUE_OFFICIAL.get(item['leagueCode'], LEAGUE_OFFICIAL['eng.1'])}, 'isAccessibleForFree': True}, ensure_ascii=False)
    script_data = json.dumps({'id': item['id'], 'leagueCode': item['leagueCode'], 'home': home, 'away': away, 'homeAr': item.get('homeAr', home), 'awayAr': item.get('awayAr', away), 'homeLogo': item.get('homeLogo', ''), 'awayLogo': item.get('awayLogo', ''), 'league': league_en, 'leagueAr': item.get('leagueAr', league_label), 'score': score, 'status': status, 'minute': item.get('minute', ''), 'time': item.get('time', ''), 'date': item.get('date', '')}, ensure_ascii=False)
    script = f'<script>window.GLOBAL_MATCH = {script_data}; window.GLOBAL_LANG = "{lang}";</script><script type="module" src="../../assets/js/match-page.js?v=1"></script>'
    return shell(lang, title, description, canonical, hreflang_for(match_path), body, script).replace('__SCHEMA__', schema)


def article_links_for_team(team, lang, fixtures):
    links = []
    for item in fixtures:
        if team.lower() in str(item.get('home', '')).lower() or team.lower() in str(item.get('away', '')).lower():
            links.append(f'<a href="../articles/{item["slug"]}.html">{esc(item["home"])} – {esc(item["away"])} · {esc(COPY[lang]["read"])}</a>')
    return ''.join(links[:8]) or f'<a href="../articles/">{esc(COPY[lang]["articles"])}</a>'


def team_page(team, fixtures, tables, lang):
    c = COPY[lang]
    slug = slugify(team)
    path = f'teams/{slug}.html'
    canonical = f'{BASE}/{lang}/{path}'
    team_matches = [item for item in fixtures if team.lower() in str(item.get('home', '')).lower() or team.lower() in str(item.get('away', '')).lower()]
    league_names = sorted({item.get('leagueEn', item.get('league', '')) for item in team_matches})
    league_name = league_names[0] if league_names else 'Premier League'
    league_label = {'ar': {'Premier League': 'الدوري الإنجليزي الممتاز', 'La Liga': 'الدوري الإسباني', 'Egyptian Premier League': 'الدوري المصري الممتاز'}.get(league_name, league_name)}.get(lang, league_name)
    title = {'ar': f'صفحة فريق {team}: المباريات والنتائج والمقالات', 'en': f'{team}: fixtures, results and match previews', 'fr': f'{team} : matchs, résultats et avant-matchs', 'es': f'{team}: partidos, resultados y previas'}[lang]
    description = {'ar': f'صفحة {team} على GlobalScore: المواعيد والنتائج والمقالات والروابط المتعلقة بالفريق.', 'en': f'GlobalScore team page for {team}: fixtures, results, previews and related coverage.', 'fr': f'Page GlobalScore de {team} : matchs, résultats, avant-matchs et couverture associée.', 'es': f'Página de GlobalScore de {team}: partidos, resultados, previas y cobertura relacionada.'}[lang]
    rows = ''.join(f'<a class="permanent-fixture-row" href="../matches/{item["id"]}.html"><span>{esc(item.get("date"))} · {esc(item.get("time"))}</span><strong>{esc(item.get("home"))} – {esc(item.get("away"))}</strong><em>{esc(item.get("status") or "Scheduled")}</em></a>' for item in team_matches)
    body = f'''{nav(lang)}<main class="page-shell permanent-page"><a class="article-back" href="../">← {esc(c['home'])}</a><section class="permanent-hero compact"><div class="permanent-kicker">{esc(c['teams'])} · {esc(league_label)}</div><h1>{esc(title)}</h1><p>{esc(description)}</p><div class="team-title-row"><span class="team-page-crest">⚽</span><div><strong>{esc(team)}</strong><small>{esc(league_label)}</small></div></div></section><section class="permanent-section"><div class="section-heading"><div><span class="section-kicker">{esc(c['upcoming'])}</span><h2>{esc(c['upcoming'])}</h2></div></div><div class="permanent-fixture-list">{rows or f'<div class="permanent-empty">{esc(c["not_available"])}</div>'}</div></section><section class="permanent-section"><div class="section-heading"><div><span class="section-kicker">{esc(c['related'])}</span><h2>{esc(c['related'])}</h2></div></div><div class="permanent-link-grid">{article_links_for_team(team, lang, fixtures)}<a href="../leagues/{slugify(league_name)}.html">{esc(c['league_page'])}: {esc(league_label)}</a></div></section></main><footer class="footer"><div class="footer-inner"><a class="brand footer-brand" href="../"><img class="logo-img" src="../../assets/img/logo.svg" alt=""><span>Global<span class="brand-accent">Score</span></span></a><p>GlobalScore Editorial</p></div></footer>'''
    schema = json.dumps({'@context': 'https://schema.org', '@type': 'SportsTeam', 'name': team, 'url': canonical, 'sport': 'Football', 'memberOf': {'@type': 'SportsOrganization', 'name': league_name}}, ensure_ascii=False)
    return shell(lang, title, description, canonical, hreflang_for(path), body).replace('__SCHEMA__', schema)


def league_page(league_name, fixtures, tables, lang):
    c = COPY[lang]
    slug = slugify(league_name)
    path = f'leagues/{slug}.html'
    canonical = f'{BASE}/{lang}/{path}'
    league_label = {'ar': {'Premier League': 'الدوري الإنجليزي الممتاز', 'La Liga': 'الدوري الإسباني', 'Egyptian Premier League': 'الدوري المصري الممتاز'}.get(league_name, league_name), 'fr': {'Premier League': 'Premier League', 'La Liga': 'La Liga', 'Egyptian Premier League': 'Championnat d’Égypte'}.get(league_name, league_name), 'es': {'Premier League': 'Premier League', 'La Liga': 'La Liga', 'Egyptian Premier League': 'Liga Premier de Egipto'}.get(league_name, league_name)}.get(lang, league_name)
    title = {'ar': f'{league_label}: المباريات والترتيب والتغطية', 'en': f'{league_label}: fixtures, standings and coverage', 'fr': f'{league_label} : matchs, classement et couverture', 'es': f'{league_label}: partidos, clasificación y cobertura'}[lang]
    description = {'ar': f'صفحة {league_label} على GlobalScore مع المباريات والترتيب والروابط التحريرية.', 'en': f'GlobalScore coverage hub for {league_label} with fixtures, standings and match previews.', 'fr': f'Hub GlobalScore de {league_label} avec matchs, classement et avant-matchs.', 'es': f'Centro de cobertura de GlobalScore para {league_label}, con partidos, clasificación y previas.'}[lang]
    league_items = [item for item in fixtures if item.get('leagueEn') == league_name]
    matches = ''.join(f'<a class="permanent-fixture-row" href="../matches/{item["id"]}.html"><span>{esc(item.get("date"))} · {esc(item.get("time"))}</span><strong>{esc(item.get("home"))} – {esc(item.get("away"))}</strong><em>{esc(item.get("status") or "Scheduled")}</em></a>' for item in league_items)
    table_rows = tables.get(league_name, [])
    if isinstance(table_rows, dict):
        table_rows = table_rows.get('rows', [])
    table_markup = ''.join(f'<tr><td>{esc(row.get("pos"))}</td><td><a href="../teams/{slugify(row.get("team") or row.get("teamAr"))}.html">{esc(row.get("team") or row.get("teamAr"))}</a></td><td>{esc(row.get("p"))}</td><td>{esc(row.get("w"))}</td><td>{esc(row.get("d"))}</td><td>{esc(row.get("l"))}</td><td><strong>{esc(row.get("pts"))}</strong></td></tr>' for row in table_rows)
    table = f'<div class="table-container permanent-table"><table class="standing-table"><thead><tr><th>#</th><th>{esc(c["teams"])}</th><th>PL</th><th>W</th><th>D</th><th>L</th><th>PTS</th></tr></thead><tbody>{table_markup}</tbody></table></div>' if table_markup else f'<div class="permanent-empty">{esc(c["not_available"])}</div>'
    body = f'''{nav(lang)}<main class="page-shell permanent-page"><a class="article-back" href="../">← {esc(c['home'])}</a><section class="permanent-hero compact"><div class="permanent-kicker">{esc(c['league'])}</div><h1>{esc(title)}</h1><p>{esc(description)}</p></section><section class="permanent-section"><div class="section-heading"><div><span class="section-kicker">{esc(c['matches'])}</span><h2>{esc(c['matches'])}</h2></div></div><div class="permanent-fixture-list">{matches or f'<div class="permanent-empty">{esc(c["not_available"])}</div>'}</div></section><section class="permanent-section"><div class="section-heading"><div><span class="section-kicker">{esc(c['table'])}</span><h2>{esc(c['standings'])}</h2></div></div>{table}</section><section class="permanent-section related-section"><div class="permanent-link-grid"><a href="{esc(LEAGUE_OFFICIAL.get(LEAGUE_CODES.get(league_name), LEAGUE_OFFICIAL['eng.1']))}" target="_blank" rel="noopener noreferrer">{esc(c['official'])}</a><a href="../articles/">{esc(c['articles'])}</a><a href="../#today">{esc(c['live'])}</a></div></section></main><footer class="footer"><div class="footer-inner"><a class="brand footer-brand" href="../"><img class="logo-img" src="../../assets/img/logo.svg" alt=""><span>Global<span class="brand-accent">Score</span></span></a><p>GlobalScore Editorial</p></div></footer>'''
    schema = json.dumps({'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': title, 'description': description, 'url': canonical, 'isAccessibleForFree': True, 'about': {'@type': 'SportsOrganization', 'name': league_name}}, ensure_ascii=False)
    return shell(lang, title, description, canonical, hreflang_for(path), body).replace('__SCHEMA__', schema)


def update_sitemap(urls):
    path = ROOT / 'Sitemap.xml'
    existing = path.read_text(encoding='utf-8') if path.exists() else ''
    existing_urls = set(re.findall(r'<loc>(.*?)</loc>', existing))
    existing_lastmods = dict(re.findall(r'<loc>(.*?)</loc>\s*<lastmod>(.*?)</lastmod>', existing))
    all_urls = sorted(existing_urls | set(urls))
    today = date.today().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in all_urls:
        lines.append(f'  <url><loc>{escape(url)}</loc><lastmod>{existing_lastmods.get(url, today)}</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>')
    lines.append('</urlset>')
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    shutil.copyfile(path, ROOT / 'sitemap.xml')
    return len(all_urls)


def main():
    fixtures, tables, updated_at = load_data()
    table_teams = set()
    for rows in tables.values():
        if isinstance(rows, dict):
            rows = rows.get('rows', [])
        for row in rows or []:
            team_name = row.get('team') or row.get('teamAr')
            if team_name:
                table_teams.add(team_name)
    teams = sorted({item.get('home') for item in fixtures} | {item.get('away') for item in fixtures} | table_teams)
    leagues = sorted({item.get('leagueEn') for item in fixtures} | {name for name in tables if name in {'Premier League', 'La Liga', 'Egyptian Premier League'}})
    urls = []
    match_count = 0
    for lang in LANGS:
        for item in fixtures:
            directory = ROOT / lang / 'matches'
            directory.mkdir(parents=True, exist_ok=True)
            (directory / f'{item["id"]}.html').write_text(match_page(item, lang), encoding='utf-8')
            urls.append(f'{BASE}/{lang}/matches/{item["id"]}.html')
            match_count += 1
        for team in teams:
            directory = ROOT / lang / 'teams'
            directory.mkdir(parents=True, exist_ok=True)
            (directory / f'{slugify(team)}.html').write_text(team_page(team, fixtures, tables, lang), encoding='utf-8')
            urls.append(f'{BASE}/{lang}/teams/{slugify(team)}.html')
        for league in leagues:
            directory = ROOT / lang / 'leagues'
            directory.mkdir(parents=True, exist_ok=True)
            (directory / f'{slugify(league)}.html').write_text(league_page(league, fixtures, tables, lang), encoding='utf-8')
            urls.append(f'{BASE}/{lang}/leagues/{slugify(league)}.html')
    sitemap_count = update_sitemap(urls)
    print(f'permanent match pages: {match_count}')
    print(f'team pages: {len(teams) * len(LANGS)}')
    print(f'league pages: {len(leagues) * len(LANGS)}')
    print(f'sitemap URLs: {sitemap_count}')
    print(f'snapshot updatedAt: {updated_at}')


if __name__ == '__main__':
    main()
