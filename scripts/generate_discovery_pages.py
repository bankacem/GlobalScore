from datetime import date
from html import escape
from pathlib import Path
import json
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://bankacem.github.io/GlobalScore'
LANGS = ('ar', 'en', 'fr', 'es')

COPY = {
    'en': {'dir': 'ltr', 'home': 'GlobalScore home', 'search': 'Search football', 'players': 'Player news', 'articles': 'Match previews', 'title_search': 'Search football matches, teams and stories', 'desc_search': 'Search GlobalScore for football matches, teams, competitions, player stories and original match previews.', 'title_players': 'Player news and analysis', 'desc_players': 'Original player-focused analysis and source-linked football news from GlobalScore.', 'placeholder': 'Search a team, player, league or article...', 'search_button': 'Search', 'results': 'Search results', 'no_results': 'No matching results yet.', 'profile': 'Player profile', 'related': 'Related coverage', 'source': 'Read the original source', 'official': 'Official reference', 'note': 'GlobalScore separates original editorial analysis from source-linked headlines. External articles open on their original website.', 'back': 'Back to GlobalScore', 'read': 'Read story', 'match': 'Match center', 'team': 'Team page', 'league': 'Competition page', 'player': 'Player analysis', 'about': 'About this page', 'performance': 'Player performance', 'performance_title': 'Performance dashboard', 'performance_intro': 'Verified season indicators from ESPN when available. Missing values are not estimated.', 'performance_loading': 'Loading verified player data…', 'performance_chart': 'Key indicators', 'performance_profile': 'Performance profile'},
    'ar': {'dir': 'rtl', 'home': 'العودة إلى GlobalScore', 'search': 'بحث كرة القدم', 'players': 'أخبار اللاعبين', 'articles': 'معاينات المباريات', 'title_search': 'ابحث عن مباريات وفرق وقصص كرة القدم', 'desc_search': 'ابحث في GlobalScore عن المباريات والفرق والمسابقات وتحليلات اللاعبين ومعاينات المباريات الأصلية.', 'title_players': 'أخبار وتحليلات اللاعبين', 'desc_players': 'تحليلات أصلية تركز على اللاعبين وأخبار مرتبطة بمصادرها من GlobalScore.', 'placeholder': 'ابحث عن فريق أو لاعب أو دوري أو مقال...', 'search_button': 'بحث', 'results': 'نتائج البحث', 'no_results': 'لا توجد نتائج مطابقة حالياً.', 'profile': 'ملف اللاعب', 'related': 'تغطية مرتبطة', 'source': 'قراءة المصدر الأصلي', 'official': 'مرجع رسمي', 'note': 'يفصل GlobalScore بين التحليل التحريري الأصلي والعناوين المرتبطة بالمصادر. تفتح المقالات الخارجية على مواقعها الأصلية.', 'back': 'العودة إلى GlobalScore', 'read': 'قراءة المقال', 'match': 'مركز المباراة', 'team': 'صفحة الفريق', 'league': 'صفحة المسابقة', 'player': 'تحليل اللاعب', 'about': 'حول هذه الصفحة', 'performance': 'أداء اللاعب', 'performance_title': 'لوحة أداء اللاعب', 'performance_intro': 'مؤشرات موسمية موثقة من ESPN عند توفرها. لا يتم تقدير القيم المفقودة.', 'performance_loading': 'جارٍ تحميل بيانات اللاعب الموثقة…', 'performance_chart': 'المؤشرات الأساسية', 'performance_profile': 'ملف الأداء'},
    'fr': {'dir': 'ltr', 'home': 'Retour à GlobalScore', 'search': 'Recherche football', 'players': 'Actualité des joueurs', 'articles': 'Avant-matchs', 'title_search': 'Rechercher des matchs, équipes et articles de football', 'desc_search': 'Recherchez dans GlobalScore des matchs, équipes, compétitions, analyses de joueurs et avant-matchs originaux.', 'title_players': 'Actualité et analyses des joueurs', 'desc_players': 'Analyses originales consacrées aux joueurs et actualités liées à leurs sources sur GlobalScore.', 'placeholder': 'Rechercher une équipe, un joueur, une compétition...', 'search_button': 'Rechercher', 'results': 'Résultats de recherche', 'no_results': 'Aucun résultat correspondant pour le moment.', 'profile': 'Profil du joueur', 'related': 'Couverture associée', 'source': 'Lire la source originale', 'official': 'Référence officielle', 'note': 'GlobalScore distingue ses analyses originales des titres liés à des sources externes. Les articles externes s’ouvrent sur leur site d’origine.', 'back': 'Retour à GlobalScore', 'read': 'Lire l’article', 'match': 'Centre du match', 'team': 'Page de l’équipe', 'league': 'Page de la compétition', 'player': 'Analyse du joueur', 'about': 'À propos de cette page', 'performance': 'Performance du joueur', 'performance_title': 'Tableau de performance', 'performance_intro': 'Indicateurs de saison vérifiés par ESPN lorsqu’ils sont disponibles. Les valeurs absentes ne sont pas estimées.', 'performance_loading': 'Chargement des données vérifiées…', 'performance_chart': 'Indicateurs clés', 'performance_profile': 'Profil de performance'},
    'es': {'dir': 'ltr', 'home': 'Volver a GlobalScore', 'search': 'Buscar fútbol', 'players': 'Noticias de jugadores', 'articles': 'Previas de partidos', 'title_search': 'Buscar partidos, equipos y artículos de fútbol', 'desc_search': 'Busca en GlobalScore partidos, equipos, competiciones, análisis de jugadores y previas originales.', 'title_players': 'Noticias y análisis de jugadores', 'desc_players': 'Análisis originales centrados en jugadores y noticias de fútbol enlazadas a sus fuentes.', 'placeholder': 'Buscar un equipo, jugador, competición o artículo...', 'search_button': 'Buscar', 'results': 'Resultados de búsqueda', 'no_results': 'Todavía no hay resultados coincidentes.', 'profile': 'Perfil del jugador', 'related': 'Cobertura relacionada', 'source': 'Leer la fuente original', 'official': 'Referencia oficial', 'note': 'GlobalScore distingue el análisis editorial original de los titulares enlazados a fuentes externas. Los artículos externos se abren en su sitio original.', 'back': 'Volver a GlobalScore', 'read': 'Leer el artículo', 'match': 'Centro del partido', 'team': 'Página del equipo', 'league': 'Página de la competición', 'player': 'Análisis del jugador', 'about': 'Sobre esta página', 'performance': 'Rendimiento del jugador', 'performance_title': 'Panel de rendimiento', 'performance_intro': 'Indicadores de temporada verificados por ESPN cuando están disponibles. Los valores ausentes no se estiman.', 'performance_loading': 'Cargando datos verificados del jugador…', 'performance_chart': 'Indicadores clave', 'performance_profile': 'Perfil de rendimiento'},
}

PLAYER = {
    'name': 'Martin Ødegaard',
    'slug': 'martin-odegaard',
    'espn_id': '203669',
    'league_code': 'eng.1',
    'title': {'en': 'Martin Ødegaard: profile, analysis and related football stories', 'ar': 'مارتن أوديجارد: الملف والتحليل والقصص المرتبطة', 'fr': 'Martin Ødegaard : profil, analyse et articles associés', 'es': 'Martin Ødegaard: perfil, análisis y artículos relacionados'},
    'description': {'en': 'GlobalScore player page for Martin Ødegaard, combining original tactical analysis with official reference links.', 'ar': 'صفحة مارتن أوديجارد على GlobalScore، تجمع التحليل التكتيكي الأصلي مع روابط المراجع الرسمية.', 'fr': 'Page GlobalScore consacrée à Martin Ødegaard, avec analyse tactique originale et références officielles.', 'es': 'Página de GlobalScore sobre Martin Ødegaard, con análisis táctico original y referencias oficiales.'},
    'intro': {'en': 'This player page focuses on observable football actions and source-backed context. It does not present unconfirmed injuries, line-ups or performance claims as facts.', 'ar': 'تركز هذه الصفحة على السلوكيات الكروية القابلة للملاحظة والسياق المدعوم بالمصادر، ولا تعرض إصابات أو تشكيلات أو أرقاماً غير مؤكدة كحقائق.', 'fr': 'Cette page se concentre sur les actions observables et un contexte appuyé par des sources. Elle ne présente pas comme faits les blessures, compositions ou performances non confirmées.', 'es': 'Esta página se centra en acciones observables y contexto respaldado por fuentes. No presenta como hechos lesiones, alineaciones o rendimientos no confirmados.'},
    'sections': {
        'en': [('A midfield role built on movement', 'Ødegaard’s influence often appears before the final pass. By adjusting his position around a compact block, he can offer the ball carrier another angle, draw a defender and help the next player receive with more time.'), ('What to watch in the next match', 'The useful questions are practical: does his movement create a lane for a winger, does the next pass change the point of attack, and can Arsenal stay connected after losing possession? These are observations rather than predictions.'), ('Editorial boundaries', 'The page links to official club and competition references. Match-specific events, line-ups and statistics should be checked on the relevant match center when they are published.')],
        'ar': [('دور في الوسط يبدأ بالحركة', 'يظهر تأثير أوديجارد أحياناً قبل التمريرة الحاسمة. فعندما يعدّل موقعه حول كتلة دفاعية متقاربة، يمنح حامل الكرة زاوية إضافية، ويجذب مدافعاً، ويساعد اللاعب التالي على الاستلام بوقت ومساحة أفضل.'), ('ما الذي يستحق المتابعة في المباراة المقبلة؟', 'الأسئلة المفيدة عملية: هل تخلق حركته ممراً للجناح؟ هل تغيّر التمريرة التالية جهة الهجوم؟ وهل يحافظ أرسنال على تقاربه بعد فقدان الكرة؟ هذه ملاحظات قابلة للفحص وليست توقعات للنتيجة.'), ('حدود التحرير', 'ترتبط الصفحة بمراجع النادي والمسابقات الرسمية. وينبغي مراجعة أحداث المباراة والتشكيلات والإحصائيات في مركز المباراة المناسب عند نشرها.')],
        'fr': [('Un rôle au milieu fondé sur le mouvement', 'L’influence d’Ødegaard apparaît souvent avant la dernière passe. En ajustant sa position autour d’un bloc compact, il offre une autre solution au porteur, attire un défenseur et aide le joueur suivant à recevoir avec davantage de temps.'), ('Les points à observer au prochain match', 'Les questions sont concrètes : son déplacement crée-t-il une ligne pour un ailier, la passe suivante change-t-elle le côté de l’attaque, et Arsenal reste-t-il compact après une perte ? Il s’agit d’observations, pas de prédictions.'), ('Limites éditoriales', 'La page renvoie vers les références officielles du club et de la compétition. Les événements, compositions et statistiques doivent être vérifiés dans le centre du match concerné lorsqu’ils sont publiés.')],
        'es': [('Un papel en el centro basado en el movimiento', 'La influencia de Ødegaard suele aparecer antes del último pase. Al ajustar su posición alrededor de un bloque compacto, ofrece otra línea al jugador con balón, atrae a un defensor y ayuda al siguiente compañero a recibir con más tiempo.'), ('Qué observar en el próximo partido', 'Las preguntas son prácticas: ¿su movimiento crea una línea para un extremo?, ¿el siguiente pase cambia el lado del ataque?, ¿el Arsenal mantiene la distancia tras perder el balón? Son observaciones, no predicciones.'), ('Límites editoriales', 'La página enlaza referencias oficiales del club y la competición. Los acontecimientos, las alineaciones y las estadísticas deben comprobarse en el centro del partido correspondiente cuando se publiquen.')],
    },
}


def slugify(value):
    normalized = unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r'[^a-z0-9]+', '-', normalized).strip('-')


def esc(value):
    return escape(str(value or ''))


def hreflang(path):
    return '\n'.join(f'<link rel="alternate" hreflang="{lang}" href="{BASE}/{lang}/{path}">' for lang in LANGS)


def common_nav(lang):
    c = COPY[lang]
    return f'''<header class="site-header"><div class="header-container"><a class="brand" href="../"><img class="logo-img" src="../../assets/img/logo.svg" alt=""><span>Global<span class="brand-accent">Score</span></span></a><nav class="nav"><a class="nav-link" href="../">{esc(c['home'])}</a><a class="nav-link" href="../articles/">{esc(c['articles'])}</a><a class="nav-link" href="../players/">{esc(c['players'])}</a><a class="nav-link" href="../search/">{esc(c['search'])}</a></nav><div class="controls"><a class="language-btn" href="../../ar/">AR</a><a class="language-btn" href="../../en/">EN</a><a class="language-btn" href="../../fr/">FR</a><a class="language-btn" href="../../es/">ES</a></div></div></header>'''


def document(lang, title, description, canonical, path, body, schema, extra=''):
    c = COPY[lang]
    return f'''<!doctype html><html lang="{lang}" dir="{c['dir']}" prefix="og: https://ogp.me/ns#"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} | GlobalScore</title><meta name="description" content="{esc(description)}"><meta name="robots" content="index,follow"><link rel="canonical" href="{canonical}">{hreflang(path)}<link rel="alternate" hreflang="x-default" href="{BASE}/en/{path}"><link rel="stylesheet" href="../../assets/css/critical.css?v=4"><link rel="stylesheet" href="../../assets/css/main.css?v=11"><meta property="og:type" content="website"><meta property="og:site_name" content="GlobalScore"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{canonical}"><meta name="twitter:card" content="summary"><script type="application/ld+json">{schema}</script></head><body>{body}{extra}</body></html>'''


def search_page(lang):
    c = COPY[lang]
    path = 'search/index.html'
    canonical = f'{BASE}/{lang}/{path}'
    body = f'''{common_nav(lang)}<main class="page-shell discovery-page"><a class="article-back" href="../">← {esc(c['home'])}</a><section class="discovery-hero"><span class="section-kicker">{esc(c['search'])}</span><h1>{esc(c['title_search'])}</h1><p>{esc(c['desc_search'])}</p><form id="globalSearchForm" class="global-search-form"><label class="sr-only" for="globalSearchInput">{esc(c['search'])}</label><input id="globalSearchInput" type="search" placeholder="{esc(c['placeholder'])}" autocomplete="off"><button class="primary-btn" type="submit">{esc(c['search_button'])}</button></form></section><section class="permanent-section" aria-live="polite"><div class="section-heading"><div><span class="section-kicker">{esc(c['results'])}</span><h2 id="searchHeading">{esc(c['results'])}</h2></div></div><div id="globalSearchResults" class="discovery-results"><div class="permanent-empty">{esc(c['no_results'])}</div></div></section></main><footer class="footer"><div class="footer-inner"><a class="brand footer-brand" href="../"><img class="logo-img" src="../../assets/img/logo.svg" alt=""><span>Global<span class="brand-accent">Score</span></span></a><p>{esc(c['note'])}</p></div></footer>'''
    schema = json.dumps({'@context': 'https://schema.org', '@type': 'WebSite', 'name': f'GlobalScore {c["search"]}', 'url': canonical, 'potentialAction': {'@type': 'SearchAction', 'target': f'{canonical}?q={{search_term_string}}', 'query-input': 'required name=search_term_string'}}, ensure_ascii=False)
    extra = f'<script>window.GLOBAL_LANG = "{lang}";</script><script type="module" src="../../assets/js/search-page.js?v=1"></script>'
    return document(lang, c['title_search'], c['desc_search'], canonical, path, body, schema, extra)


def player_page(lang):
    c = COPY[lang]
    path = f'players/{PLAYER["slug"]}.html'
    canonical = f'{BASE}/{lang}/{path}'
    title = PLAYER['title'][lang]
    description = PLAYER['description'][lang]
    section_markup = ''.join(f'<section class="player-analysis-block"><h2>{esc(heading)}</h2><p>{esc(text)}</p></section>' for heading, text in PLAYER['sections'][lang])
    article_href = f'../articles/player-watch-odegaard.html'
    body = f'''{common_nav(lang)}<main class="page-shell discovery-page"><a class="article-back" href="../players/">← {esc(c['players'])}</a><section class="discovery-hero player-hero"><span class="section-kicker">{esc(c['profile'])}</span><h1>{esc(title)}</h1><p>{esc(PLAYER['intro'][lang])}</p><div class="player-identity"><span class="team-page-crest">⚽</span><strong>{esc(PLAYER['name'])}</strong></div></section><section class="performance-panel" id="playerPerformance" data-player-id="{PLAYER['espn_id']}" data-league-code="{PLAYER['league_code']}"><div class="section-heading"><div><span class="section-kicker">{esc(c['performance'])}</span><h2>{esc(c['performance_title'])}</h2></div></div><p class="performance-intro">{esc(c['performance_intro'])}</p><div id="playerPerformanceStatus" class="performance-status">{esc(c['performance_loading'])}</div><div id="playerPerformanceKpis" class="performance-kpis"></div><div class="performance-visuals"><div class="performance-chart-card"><h3>{esc(c['performance_chart'])}</h3><div id="playerPerformanceBars" class="performance-bars"></div></div><div class="performance-radar-card"><h3>{esc(c['performance_profile'])}</h3><div id="playerPerformanceRadar" class="performance-radar"></div></div></div><p id="playerPerformanceSource" class="performance-source"></p></section><article class="player-analysis-card">{section_markup}</article><section class="permanent-section"><div class="section-heading"><div><span class="section-kicker">{esc(c['related'])}</span><h2>{esc(c['related'])}</h2></div></div><div class="permanent-link-grid"><a href="{article_href}">{esc(c['player'])}: Martin Ødegaard</a><a href="../teams/arsenal.html">{esc(c['team'])}: Arsenal</a><a href="https://www.arsenal.com/men/players/martin-odegaard" target="_blank" rel="noopener noreferrer">{esc(c['official'])}: Arsenal</a><a href="https://www.premierleague.com/en/players/184029/martin-degaard/overview" target="_blank" rel="noopener noreferrer">{esc(c['official'])}: Premier League</a></div></section><p class="permanent-source-note">{esc(c['note'])}</p></main><footer class="footer"><div class="footer-inner"><a class="brand footer-brand" href="../"><img class="logo-img" src="../../assets/img/logo.svg" alt=""><span>Global<span class="brand-accent">Score</span></span></a><p>GlobalScore Editorial</p></div></footer>'''
    schema = json.dumps({'@context': 'https://schema.org', '@type': 'ProfilePage', 'name': title, 'description': description, 'url': canonical, 'mainEntity': {'@type': 'Person', 'name': PLAYER['name'], 'jobTitle': 'Footballer'}}, ensure_ascii=False)
    extra = f'<script>window.GLOBAL_LANG = "{lang}";</script><script type="module" src="../../assets/js/player-performance.js?v=1"></script>'
    return document(lang, title, description, canonical, path, body, schema, extra)


def players_index(lang, articles):
    c = COPY[lang]
    path = 'players/index.html'
    canonical = f'{BASE}/{lang}/{path}'
    player_href = f'{PLAYER["slug"]}.html'
    source_cards = []
    for article in articles:
        if article.get('external') and ('player' in str(article.get('category', '')).lower() or 'rating' in str(article.get('title', '')).lower()):
            title = article.get('titleAr') if lang == 'ar' else article.get('title')
            excerpt = article.get('excerptAr') if lang == 'ar' else article.get('excerpt')
            source_cards.append(f'<a class="discovery-card" href="{esc(article.get("href"))}" target="_blank" rel="noopener noreferrer"><div class="news-meta"><span class="news-tag">{esc(c["players"])}</span><span>{esc(article.get("source") or "RSS")}</span></div><h3>{esc(title)}</h3><p>{esc(excerpt)}</p><span class="news-arrow">↗</span></a>')
    source_markup = ''.join(source_cards) or f'<div class="permanent-empty">{esc(c["no_results"])}</div>'
    title = c['title_players']
    description = c['desc_players']
    body = f'''{common_nav(lang)}<main class="page-shell discovery-page"><a class="article-back" href="../">← {esc(c['home'])}</a><section class="discovery-hero"><span class="section-kicker">{esc(c['players'])}</span><h1>{esc(title)}</h1><p>{esc(description)}</p></section><section class="permanent-section"><div class="section-heading"><div><span class="section-kicker">{esc(c['profile'])}</span><h2>{esc(c['profile'])}</h2></div></div><div class="discovery-grid"><a class="discovery-card player-card" href="{player_href}"><div class="player-identity"><span class="team-page-crest">⚽</span><strong>Martin Ødegaard</strong></div><p>{esc(PLAYER['intro'][lang])}</p><span class="news-arrow">→</span></a></div></section><section class="permanent-section"><div class="section-heading"><div><span class="section-kicker">{esc(c['source'])}</span><h2>{esc(c['players'])}</h2></div></div><div class="discovery-grid">{source_markup}</div></section><p class="permanent-source-note">{esc(c['note'])}</p></main><footer class="footer"><div class="footer-inner"><a class="brand footer-brand" href="../"><img class="logo-img" src="../../assets/img/logo.svg" alt=""><span>Global<span class="brand-accent">Score</span></span></a><p>GlobalScore Editorial</p></div></footer>'''
    schema = json.dumps({'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': title, 'description': description, 'url': canonical, 'isAccessibleForFree': True}, ensure_ascii=False)
    return document(lang, title, description, canonical, path, body, schema)


def main():
    content = json.loads((ROOT / 'assets/data/content.json').read_text(encoding='utf-8'))
    articles = content.get('articles', [])
    urls = []
    for lang in LANGS:
        for subdir in ('search', 'players'):
            (ROOT / lang / subdir).mkdir(parents=True, exist_ok=True)
        (ROOT / lang / 'search/index.html').write_text(search_page(lang), encoding='utf-8')
        (ROOT / lang / 'players/index.html').write_text(players_index(lang, articles), encoding='utf-8')
        (ROOT / lang / f'players/{PLAYER["slug"]}.html').write_text(player_page(lang), encoding='utf-8')
        urls.extend([f'{BASE}/{lang}/search/index.html', f'{BASE}/{lang}/players/index.html', f'{BASE}/{lang}/players/{PLAYER["slug"]}.html'])
    sitemap_path = ROOT / 'Sitemap.xml'
    sitemap = sitemap_path.read_text(encoding='utf-8') if sitemap_path.exists() else ''
    blocks = {}
    for block in re.findall(r'<url>.*?</url>', sitemap, flags=re.S):
        loc_match = re.search(r'<loc>(.*?)</loc>', block, flags=re.S)
        if loc_match:
            blocks[loc_match.group(1)] = block.strip()
    today = date.today().isoformat()
    for url in urls:
        if url not in blocks:
            blocks[url] = f'<url><loc>{escape(url)}</loc><lastmod>{today}</lastmod><changefreq>daily</changefreq><priority>0.6</priority></url>'
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    lines.extend(f'  {blocks[url]}' for url in sorted(blocks))
    lines.append('</urlset>')
    sitemap_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    (ROOT / 'sitemap.xml').write_text(sitemap_path.read_text(encoding='utf-8'), encoding='utf-8')
    print(f'discovery pages: {len(urls)}')
    print(f'sitemap URLs: {len(blocks)}')


if __name__ == '__main__':
    main()
