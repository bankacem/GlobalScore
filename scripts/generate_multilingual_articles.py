from datetime import date, datetime, timezone, timedelta
from html import escape
from pathlib import Path
import json
import re
import shutil
import unicodedata
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://bankacem.github.io/GlobalScore'
LANGS = ('ar', 'en', 'fr', 'es')
LEAGUES = (
    ('eng.1', 'Premier League', 'الدوري الإنجليزي الممتاز', 'Premier League', 'Premier League'),
    ('esp.1', 'La Liga', 'الدوري الإسباني', 'La Liga', 'La Liga'),
    ('uefa.champions', 'UEFA Champions League', 'دوري أبطال أوروبا', 'Ligue des champions', 'Liga de Campeones'),
    ('egy.1', 'Egyptian Premier League', 'الدوري المصري الممتاز', 'Championnat d’Égypte', 'Liga Premier de Egipto'),
)


def slugify(value):
    normalized = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r'[^a-z0-9]+', '-', normalized).strip('-')


def fetch_json(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'GlobalScore editorial bot/1.0'})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def fixture_from_event(event, league, day):
    competition = (event.get('competitions') or [{}])[0]
    competitors = competition.get('competitors') or []
    home = next((item for item in competitors if item.get('homeAway') == 'home'), competitors[0] if competitors else {})
    away = next((item for item in competitors if item.get('homeAway') == 'away'), competitors[1] if len(competitors) > 1 else {})
    status_name = competition.get('status', {}).get('type', {}).get('name', '')
    if status_name in {'STATUS_FULL_TIME', 'STATUS_FINAL', 'STATUS_IN_PROGRESS', 'STATUS_HALFTIME', 'STATUS_END_PERIOD'}:
        return None
    home_name = home.get('team', {}).get('displayName')
    away_name = away.get('team', {}).get('displayName')
    if not home_name or not away_name:
        return None
    start = event.get('date', '')
    start_time = start[11:16] if len(start) >= 16 else '--:--'
    slug = f"{day.isoformat()}-{slugify(home_name)}-{slugify(away_name)}"
    return {
        'event_id': str(event.get('id') or ''),
        'match_key': str(event.get('id') or f'{day.isoformat()}:{slugify(home_name)}:{slugify(away_name)}'),
        'slug': slug,
        'home': home_name,
        'away': away_name,
        'league': {'en': league[1], 'ar': league[2], 'fr': league[3], 'es': league[4]},
        'league_code': league[0],
        'date': day.isoformat(),
        'time': f'{start_time} UTC',
        'angle': 0,
    }


def fetch_dynamic_fixtures():
    today = datetime.now(timezone.utc).date()
    found = []
    for offset, day in enumerate((today, today + timedelta(days=1))):
        for league in LEAGUES:
            url = f'https://site.api.espn.com/apis/site/v2/sports/soccer/{league[0]}/scoreboard?dates={day.strftime("%Y%m%d")}'
            try:
                payload = fetch_json(url)
            except Exception as exc:
                print(f'warning: ESPN fixture fetch failed for {league[0]} {day}: {exc}')
                continue
            for event in payload.get('events', []):
                fixture = fixture_from_event(event, league, day)
                if fixture:
                    fixture['angle'] = (len(found) + offset) % 10
                    found.append(fixture)
    unique = []
    seen = set()
    for fixture in sorted(found, key=lambda item: (item['date'], item['time'], item['home'])):
        key = fixture['event_id'] or fixture['match_key']
        if key not in seen:
            seen.add(key)
            unique.append(fixture)
    return unique[:10]


def load_snapshot_fixtures():
    candidates = []
    for path in (ROOT / 'assets/data/content.json', ROOT / 'assets/data/live.json'):
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            continue
        candidates.extend(payload.get('fixtures', []) if path.name == 'content.json' else payload.get('matches', []))
    today = datetime.now(timezone.utc).date()
    allowed_days = {today, today + timedelta(days=1)}
    result = []
    seen = set()
    league_map = {item[1]: item for item in LEAGUES}
    for item in candidates:
        if str(item.get('status', '')).upper() in {'FT', 'FINAL', 'FINISHED', 'CANCELLED', 'POSTPONED'}:
            continue
        home = item.get('home') or item.get('strHomeTeam')
        away = item.get('away') or item.get('strAwayTeam')
        if not home or not away:
            continue
        raw_date = item.get('date') or today.isoformat()
        try:
            match_day = date.fromisoformat(str(raw_date)[:10])
        except ValueError:
            match_day = today
        if match_day not in allowed_days:
            continue
        league_name = item.get('league') or 'Premier League'
        league = league_map.get(league_name, LEAGUES[0])
        match_key = str(item.get('id') or f'{match_day.isoformat()}:{slugify(home)}:{slugify(away)}')
        if match_key in seen:
            continue
        seen.add(match_key)
        result.append({'event_id': str(item.get('id') or ''), 'match_key': f'snapshot:{match_key}', 'slug': f'{match_day.isoformat()}-{slugify(home)}-{slugify(away)}', 'home': home, 'away': away, 'league': {'en': league[1], 'ar': league[2], 'fr': league[3], 'es': league[4]}, 'league_code': league[0], 'date': match_day.isoformat(), 'time': f"{item.get('time') or '--:--'} UTC", 'angle': len(result) % 10})
    return result[:10]


FALLBACK_FIXTURES = [
    {'event_id': '', 'match_key': 'fallback:hull-city:manchester-united', 'slug': 'hull-city-manchester-united', 'home': 'Hull City', 'away': 'Manchester United', 'league': {'en': 'Premier League', 'ar': 'الدوري الإنجليزي الممتاز', 'fr': 'Premier League', 'es': 'Premier League'}, 'league_code': 'eng.1', 'date': '2026-08-22', 'time': '11:30 UTC', 'angle': 0},
    {'event_id': '', 'match_key': 'fallback:everton:crystal-palace', 'slug': 'everton-crystal-palace', 'home': 'Everton', 'away': 'Crystal Palace', 'league': {'en': 'Premier League', 'ar': 'الدوري الإنجليزي الممتاز', 'fr': 'Premier League', 'es': 'Premier League'}, 'league_code': 'eng.1', 'date': '2026-08-22', 'time': '14:00 UTC', 'angle': 1},
]

try:
    fixtures = fetch_dynamic_fixtures()
except Exception as exc:
    print(f'warning: dynamic fixture generation failed: {exc}')
    fixtures = []
if len(fixtures) < 1:
    fixtures = load_snapshot_fixtures()
if len(fixtures) < 1:
    fixtures = FALLBACK_FIXTURES

COPY = {
    'en': {'dir': 'ltr', 'back': 'Back to GlobalScore', 'tag': 'MATCH PREVIEW', 'read': '6 min read', 'date_label': 'Match date', 'time_label': 'Kick-off', 'league_label': 'Competition', 'focus': 'What to watch', 'questions': 'Three questions before kick-off', 'details': 'Live match details', 'details_text': 'When the match starts, GlobalScore will update the score, minute, events, lineups, referee and venue details from the available live data source.', 'source': 'Fixture and live data: ESPN scoreboard.', 'home_label': 'Home', 'away_label': 'Away', 'cta': 'Open the live scoreboard', 'seo': 'match preview, live score, lineups, referee, stadium, football news'},
    'ar': {'dir': 'rtl', 'back': 'العودة إلى GlobalScore', 'tag': 'معاينة المباراة', 'read': '6 دقائق للقراءة', 'date_label': 'تاريخ المباراة', 'time_label': 'موعد البداية', 'league_label': 'المسابقة', 'focus': 'ما الذي يستحق المتابعة؟', 'questions': 'ثلاثة أسئلة قبل البداية', 'details': 'تفاصيل المباراة المباشرة', 'details_text': 'عند انطلاق المباراة، سيحدّث GlobalScore النتيجة والدقيقة والأحداث والتشكيلات والحكم والملعب وفق البيانات الحية المتاحة.', 'source': 'بيانات الموعد والبث المباشر: لوحة نتائج ESPN.', 'home_label': 'صاحب الأرض', 'away_label': 'الضيف', 'cta': 'فتح لوحة النتائج المباشرة', 'seo': 'معاينة المباراة، نتيجة مباشرة، التشكيلة، الحكم، الملعب، أخبار كرة القدم'},
    'fr': {'dir': 'ltr', 'back': 'Retour à GlobalScore', 'tag': 'AVANT-MATCH', 'read': '6 min de lecture', 'date_label': 'Date du match', 'time_label': 'Coup d’envoi', 'league_label': 'Compétition', 'focus': 'Le point à surveiller', 'questions': 'Trois questions avant le coup d’envoi', 'details': 'Détails du match en direct', 'details_text': 'Au coup d’envoi, GlobalScore mettra à jour le score, la minute, les événements, les compositions, l’arbitre et le stade selon les données disponibles.', 'source': 'Données du calendrier et du direct : tableau des scores ESPN.', 'home_label': 'Domicile', 'away_label': 'Extérieur', 'cta': 'Ouvrir le tableau des scores', 'seo': 'avant-match, score en direct, compositions, arbitre, stade, actualité football'},
    'es': {'dir': 'ltr', 'back': 'Volver a GlobalScore', 'tag': 'PREVIA DEL PARTIDO', 'read': '6 min de lectura', 'date_label': 'Fecha del partido', 'time_label': 'Inicio', 'league_label': 'Competición', 'focus': 'La clave del partido', 'questions': 'Tres preguntas antes del inicio', 'details': 'Detalles del partido en directo', 'details_text': 'Cuando comience el partido, GlobalScore actualizará el marcador, el minuto, los eventos, las alineaciones, el árbitro y el estadio según los datos disponibles.', 'source': 'Datos del calendario y directo: marcador de ESPN.', 'home_label': 'Local', 'away_label': 'Visitante', 'cta': 'Abrir el marcador en directo', 'seo': 'previa del partido, resultado en directo, alineaciones, árbitro, estadio, noticias de fútbol'},
}

ANGLES = {
    'en': ['The opening phase should set the rhythm, with both sides looking for control before taking greater risks.', 'The central areas may decide the tempo, especially when possession changes hands.', 'Transitions can shape the decisive moments as each team searches for space behind the first line.', 'The defensive test is as important as the attacking promise: distances and patience will matter.', 'Set pieces and second balls offer a practical route to momentum in a fixture that may be decided by details.', 'This match is an early test of pressing, control and the ability to protect a lead.', 'The key question is how the favourite manages territory while the challenger looks for forward exits.', 'Intensity and decision-making could change the story quickly if the match becomes stretched.', 'The tactical contrast should be compelling, with structure facing movement and variation.', 'The fixture presents a clear balance question: how much risk can each side take without losing control.'],
    'ar': ['ستكون المرحلة الأولى مهمة؛ إذ يحتاج الطرفان إلى إيقاع واضح قبل رفع مستوى المخاطرة.', 'قد تحدد مناطق الوسط سرعة اللعب، خصوصاً عند انتقال الاستحواذ من فريق إلى آخر.', 'يمكن أن تحسم التحولات أهم اللحظات، مع بحث كل فريق عن المساحات خلف خط الضغط الأول.', 'الاختبار الدفاعي لا يقل أهمية عن الوعود الهجومية؛ فالصبر والمسافات قد يصنعان الفارق.', 'تمنح الكرات الثابتة والكرات الثانية طريقاً عملياً لصناعة الزخم في مباراة قد تحسمها التفاصيل.', 'تمثل المواجهة اختباراً للسيطرة والضغط والقدرة على حماية التقدم.', 'سيتركز الاهتمام على طريقة إدارة الفريق المرشح للمساحات، وعلى فرص المنافس في الخروج للأمام.', 'قد تغيّر جودة القرارات وارتفاع الإيقاع قصة اللقاء بسرعة.', 'يوحي اللقاء بتباين تكتيكي جذاب، بين التنظيم والحركة وتغيير مراكز اللعب.', 'تطرح المباراة سؤالاً واضحاً حول التوازن والمخاطرة دون فقدان السيطرة.'],
    'fr': ['La première phase sera importante : les deux équipes devront trouver leur rythme avant de prendre davantage de risques.', 'Les zones centrales devraient déterminer le tempo, surtout lors des changements de possession.', 'Les transitions peuvent décider des moments clés, chaque équipe cherchant l’espace derrière le premier rideau.', 'Le test défensif est aussi important que la promesse offensive : patience et distances seront essentielles.', 'Les coups de pied arrêtés et les seconds ballons peuvent créer l’élan dans un match décidé par les détails.', 'Cette rencontre sera un test du contrôle, du pressing et de la capacité à protéger un avantage.', 'L’attention se portera sur la gestion du territoire par le favori et les sorties de son adversaire.', 'L’intensité et la qualité des décisions peuvent changer le scénario très vite.', 'Le contraste tactique devrait rendre le duel intéressant, entre structure, mouvement et variations.', 'La rencontre pose une question d’équilibre : quel risque prendre sans perdre le contrôle ?'],
    'es': ['La primera fase será importante: ambos equipos necesitarán encontrar su ritmo antes de asumir más riesgos.', 'Las zonas centrales pueden marcar el ritmo, especialmente cuando cambia la posesión.', 'Las transiciones pueden decidir los momentos clave, con ambos equipos buscando espacios detrás de la primera línea.', 'El examen defensivo es tan importante como la promesa ofensiva: la paciencia y las distancias serán decisivas.', 'Las acciones a balón parado y las segundas jugadas ofrecen una vía práctica para ganar impulso.', 'El encuentro será una prueba de control, presión y capacidad para proteger una ventaja.', 'La atención estará en cómo el favorito gestiona el territorio y cómo el rival encuentra salidas.', 'La intensidad y la toma de decisiones pueden cambiar la historia rápidamente.', 'El contraste táctico promete un duelo atractivo entre estructura, movimiento y variación.', 'El partido plantea una pregunta de equilibrio: asumir riesgos sin perder el control.'],
}

QUESTIONS = {
    'en': ['Who controls the first pass after winning the ball?', 'Can either side turn territorial pressure into clear chances?', 'Which team adapts better if the opening plan stops working?'],
    'ar': ['من يسيطر على التمريرة الأولى بعد استعادة الكرة؟', 'هل يستطيع أي طرف تحويل الضغط الميداني إلى فرص واضحة؟', 'أي فريق سيتكيف بشكل أفضل إذا لم تنجح الخطة الأولى؟'],
    'fr': ['Qui contrôlera la première passe après la récupération ?', 'Une équipe peut-elle transformer sa pression territoriale en occasions nettes ?', 'Qui s’adaptera le mieux si le plan initial ne fonctionne pas ?'],
    'es': ['¿Quién controlará el primer pase tras recuperar el balón?', '¿Puede alguno convertir la presión territorial en ocasiones claras?', '¿Qué equipo se adaptará mejor si el plan inicial deja de funcionar?'],
}


def page_for(fixture, lang):
    c = COPY[lang]
    slug = fixture['slug']
    title = {
        'en': f"{fixture['home']} vs {fixture['away']}: match preview, time and key questions",
        'ar': f"معاينة مباراة {fixture['home']} و{fixture['away']}: الموعد وأبرز الأسئلة",
        'fr': f"{fixture['home']} - {fixture['away']} : avant-match, horaire et enjeux",
        'es': f"{fixture['home']} - {fixture['away']}: previa, horario y claves",
    }[lang]
    description = {
        'en': f"{fixture['home']} and {fixture['away']} meet in the {fixture['league']['en']} on {fixture['date']}. This original preview explains the context without inventing line-ups or confirmed player news.",
        'ar': f"يلتقي {fixture['home']} و{fixture['away']} في {fixture['league']['ar']} يوم {fixture['date']}. تقدم هذه المعاينة الأصلية سياق اللقاء دون اختلاق تشكيلات أو أخبار مؤكدة عن اللاعبين.",
        'fr': f"{fixture['home']} et {fixture['away']} se retrouvent en {fixture['league']['fr']} le {fixture['date']}. Cette analyse originale présente le contexte sans inventer de compositions ni d’informations confirmées.",
        'es': f"{fixture['home']} y {fixture['away']} se enfrentan en {fixture['league']['es']} el {fixture['date']}. Esta previa original analiza el contexto sin inventar alineaciones ni noticias confirmadas.",
    }[lang]
    canonical = f'{BASE}/{lang}/articles/{slug}.html'
    hreflang = '\n'.join(f'<link rel="alternate" hreflang="{code}" href="{BASE}/{code}/articles/{slug}.html">' for code in LANGS)
    questions = ''.join(f'<li>{escape(q)}</li>' for q in QUESTIONS[lang])
    table = f'<div class="article-fact-grid"><div><small>{c["home_label"]}</small><strong>{escape(fixture["home"])}</strong></div><div><small>{c["away_label"]}</small><strong>{escape(fixture["away"])}</strong></div><div><small>{c["league_label"]}</small><strong>{escape(fixture["league"][lang])}</strong></div><div><small>{c["date_label"]}</small><strong>{escape(fixture["date"])}</strong></div><div><small>{c["time_label"]}</small><strong>{escape(fixture["time"])}</strong></div></div>'
    paragraphs = [description, ANGLES[lang][fixture['angle'] % len(ANGLES[lang])], c['details_text']]
    body = ''.join(f'<p>{escape(paragraph)}</p>' for paragraph in paragraphs)
    schema = json.dumps({'@context': 'https://schema.org', '@type': 'Article', 'headline': title, 'description': description, 'datePublished': fixture['date'], 'dateModified': datetime.now(timezone.utc).date().isoformat(), 'author': {'@type': 'Organization', 'name': 'GlobalScore Editorial'}, 'publisher': {'@type': 'Organization', 'name': 'GlobalScore'}, 'mainEntityOfPage': {'@type': 'WebPage', '@id': canonical}, 'isAccessibleForFree': True}, ensure_ascii=False)
    return f'''<!doctype html><html lang="{lang}" dir="{c['dir']}" prefix="og: https://ogp.me/ns#"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)} | GlobalScore</title><meta name="description" content="{escape(description)}"><meta name="keywords" content="{escape(c['seo'])}"><link rel="canonical" href="{canonical}">{hreflang}<link rel="stylesheet" href="../../assets/css/critical.css?v=4"><link rel="stylesheet" href="../../assets/css/main.css?v=7"><meta property="og:type" content="article"><meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(description)}"><meta property="og:url" content="{canonical}"><script type="application/ld+json">{schema}</script></head><body><header class="site-header"><div class="header-container"><a class="brand" href="../../{lang}/"><img class="logo-img" src="../../assets/img/logo.svg" alt=""><span>Global<span class="brand-accent">Score</span></span></a><nav class="nav"><a class="nav-link" href="../../{lang}/">{c['back']}</a></nav><div class="controls"><a class="language-btn" href="../../ar/articles/{slug}.html">AR</a><a class="language-btn" href="../../en/articles/{slug}.html">EN</a><a class="language-btn" href="../../fr/articles/{slug}.html">FR</a><a class="language-btn" href="../../es/articles/{slug}.html">ES</a></div></div></header><main class="page-shell"><article class="article-page"><header class="article-header"><a class="article-back" href="../../{lang}/">← {c['back']}</a><span class="section-kicker">{c['tag']}</span><h1>{escape(title)}</h1><p class="article-dek">{escape(description)}</p><div class="article-meta"><span>{c['read']}</span><span>{escape(fixture['date'])}</span><span>GlobalScore Editorial</span></div></header><div class="article-content">{table}<h2>{c['focus']}</h2>{body}<h2>{c['questions']}</h2><ol>{questions}</ol><h2>{c['details']}</h2><p>{escape(c['details_text'])}</p><p class="article-note">{escape(c['source'])}</p><p><a class="primary-btn" href="../../{lang}/#today">{c['cta']} <span>→</span></a></p></div></article></main><footer class="footer"><div class="footer-inner"><a class="brand footer-brand" href="../../{lang}/"><img class="logo-img" src="../../assets/img/logo.svg" alt=""><span>Global<span class="brand-accent">Score</span></span></a><p>GlobalScore Editorial</p><div class="footer-links"><a href="../../ar/articles/{slug}.html">العربية</a><a href="../../en/articles/{slug}.html">English</a><a href="../../fr/articles/{slug}.html">Français</a><a href="../../es/articles/{slug}.html">Español</a></div></div></footer></body></html>'''


def landing(lang):
    c = COPY[lang]
    headings = {'en': 'Football previews for today and tomorrow', 'ar': 'معاينات مباريات اليوم والغد', 'fr': 'Avant-matchs du jour et du lendemain', 'es': 'Previas de los partidos de hoy y mañana'}
    intro = {'en': 'Original, source-aware match briefings with clear times and live-data links.', 'ar': 'معاينات أصلية للمباريات مع المواعيد وروابط البيانات الحية.', 'fr': 'Des avant-matchs originaux avec horaires clairs et liens vers les données en direct.', 'es': 'Previas originales con horarios claros y enlaces a los datos en directo.'}
    cards = ''.join(f'<a class="news-card" href="{f["slug"]}.html"><div class="news-meta"><span class="news-tag">{escape(c["tag"])}</span><span>{escape(f["date"])}</span></div><h2>{escape(f["home"] + " – " + f["away"])}</h2><p>{escape(f["league"][lang])} · {escape(f["time"])}</p><span class="news-arrow">→</span></a>' for f in fixtures)
    return f'''<!doctype html><html lang="{lang}" dir="{c['dir']}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>GlobalScore | {headings[lang]}</title><meta name="description" content="{intro[lang]}"><link rel="canonical" href="{BASE}/{lang}/articles/"><link rel="alternate" hreflang="ar" href="{BASE}/ar/articles/"><link rel="alternate" hreflang="en" href="{BASE}/en/articles/"><link rel="alternate" hreflang="fr" href="{BASE}/fr/articles/"><link rel="alternate" hreflang="es" href="{BASE}/es/articles/"><link rel="stylesheet" href="../../assets/css/critical.css?v=4"><link rel="stylesheet" href="../../assets/css/main.css?v=7"></head><body><header class="site-header"><div class="header-container"><a class="brand" href="../../{lang}/"><img class="logo-img" src="../../assets/img/logo.svg" alt=""><span>Global<span class="brand-accent">Score</span></span></a><div class="controls"><a class="language-btn" href="../../ar/articles/">AR</a><a class="language-btn" href="../../en/articles/">EN</a><a class="language-btn" href="../../fr/articles/">FR</a><a class="language-btn" href="../../es/articles/">ES</a></div></div></header><main class="page-shell"><section class="hero-panel"><div class="hero-copy"><span class="eyebrow">GLOBAL SCORE EDITORIAL</span><h1>{headings[lang]}</h1><p>{intro[lang]}</p></div></section><section class="content-section"><div class="section-heading"><div><span class="section-kicker">{c['tag']}</span><h2>{headings[lang]}</h2></div></div><div class="news-grid">{cards}</div></section></main><footer class="footer"><div class="footer-inner"><a class="brand footer-brand" href="../../{lang}/"><img class="logo-img" src="../../assets/img/logo.svg" alt=""><span>Global<span class="brand-accent">Score</span></span></a><div class="footer-links"><a href="../../ar/">العربية</a><a href="../../en/">English</a><a href="../../fr/">Français</a><a href="../../es/">Español</a></div></div></footer></body></html>'''


registry_path = ROOT / 'assets/data/article_registry.json'
try:
    registry = json.loads(registry_path.read_text(encoding='utf-8')) if registry_path.exists() else {}
except json.JSONDecodeError:
    registry = {}
now = datetime.now(timezone.utc).isoformat()
for fixture in fixtures:
    key = fixture['match_key']
    registry[key] = {'eventId': fixture['event_id'], 'slug': fixture['slug'], 'date': fixture['date'], 'home': fixture['home'], 'away': fixture['away'], 'lastGenerated': now, 'languages': list(LANGS)}

for lang in LANGS:
    article_dir = ROOT / lang / 'articles'
    article_dir.mkdir(parents=True, exist_ok=True)
    for fixture in fixtures:
        (article_dir / f"{fixture['slug']}.html").write_text(page_for(fixture, lang), encoding='utf-8')
    (article_dir / 'index.html').write_text(landing(lang), encoding='utf-8')

registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

sitemap_path = ROOT / 'Sitemap.xml'
existing = sitemap_path.read_text(encoding='utf-8') if sitemap_path.exists() else ''
existing_urls = set(re.findall(r'<loc>(.*?)</loc>', existing))
new_urls = {f'{BASE}/{lang}/articles/{fixture["slug"]}.html' for lang in LANGS for fixture in fixtures}
new_urls |= {f'{BASE}/{lang}/articles/' for lang in LANGS}
new_urls |= {f'{BASE}/{lang}/' for lang in LANGS}
all_urls = sorted(existing_urls | new_urls)
lastmod = date.today().isoformat()
xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
xml += [f'  <url><loc>{escape(url)}</loc><lastmod>{lastmod}</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>' for url in all_urls]
xml.append('</urlset>')
sitemap_path.write_text('\n'.join(xml) + '\n', encoding='utf-8')
shutil.copyfile(sitemap_path, ROOT / 'sitemap.xml')

print(f'generated_or_updated {len(fixtures)} fixtures x {len(LANGS)} languages = {len(fixtures) * len(LANGS)} pages')
print(f'registry records: {len(registry)}')
print(f'sitemap URLs: {len(all_urls)}')
