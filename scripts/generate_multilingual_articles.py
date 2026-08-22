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
TODAY = date(2026, 8, 22)

fixtures = [
    {'slug': 'hull-city-manchester-united', 'home': 'Hull City', 'away': 'Manchester United', 'league': {'en': 'Premier League', 'ar': 'الدوري الإنجليزي الممتاز', 'fr': 'Premier League', 'es': 'Premier League'}, 'date': '2026-08-22', 'time': '11:30 UTC', 'angle': 0},
    {'slug': 'everton-crystal-palace', 'home': 'Everton', 'away': 'Crystal Palace', 'league': {'en': 'Premier League', 'ar': 'الدوري الإنجليزي الممتاز', 'fr': 'Premier League', 'es': 'Premier League'}, 'date': '2026-08-22', 'time': '14:00 UTC', 'angle': 1},
    {'slug': 'ipswich-town-sunderland', 'home': 'Ipswich Town', 'away': 'Sunderland', 'league': {'en': 'Premier League', 'ar': 'الدوري الإنجليزي الممتاز', 'fr': 'Premier League', 'es': 'Premier League'}, 'date': '2026-08-22', 'time': '14:00 UTC', 'angle': 2},
    {'slug': 'nottingham-forest-leeds-united', 'home': 'Nottingham Forest', 'away': 'Leeds United', 'league': {'en': 'Premier League', 'ar': 'الدوري الإنجليزي الممتاز', 'fr': 'Premier League', 'es': 'Premier League'}, 'date': '2026-08-22', 'time': '14:00 UTC', 'angle': 3},
    {'slug': 'brentford-tottenham-hotspur', 'home': 'Brentford', 'away': 'Tottenham Hotspur', 'league': {'en': 'Premier League', 'ar': 'الدوري الإنجليزي الممتاز', 'fr': 'Premier League', 'es': 'Premier League'}, 'date': '2026-08-22', 'time': '16:30 UTC', 'angle': 4},
    {'slug': 'brighton-aston-villa', 'home': 'Brighton & Hove Albion', 'away': 'Aston Villa', 'league': {'en': 'Premier League', 'ar': 'الدوري الإنجليزي الممتاز', 'fr': 'Premier League', 'es': 'Premier League'}, 'date': '2026-08-23', 'time': '13:00 UTC', 'angle': 5},
    {'slug': 'manchester-city-bournemouth', 'home': 'Manchester City', 'away': 'AFC Bournemouth', 'league': {'en': 'Premier League', 'ar': 'الدوري الإنجليزي الممتاز', 'fr': 'Premier League', 'es': 'Premier League'}, 'date': '2026-08-23', 'time': '13:00 UTC', 'angle': 6},
    {'slug': 'newcastle-united-liverpool', 'home': 'Newcastle United', 'away': 'Liverpool', 'league': {'en': 'Premier League', 'ar': 'الدوري الإنجليزي الممتاز', 'fr': 'Premier League', 'es': 'Premier League'}, 'date': '2026-08-23', 'time': '15:30 UTC', 'angle': 7},
    {'slug': 'atletico-madrid-villarreal', 'home': 'Atlético Madrid', 'away': 'Villarreal', 'league': {'en': 'La Liga', 'ar': 'الدوري الإسباني', 'fr': 'La Liga', 'es': 'La Liga'}, 'date': '2026-08-23', 'time': '15:00 UTC', 'angle': 8},
    {'slug': 'elche-barcelona', 'home': 'Elche', 'away': 'Barcelona', 'league': {'en': 'La Liga', 'ar': 'الدوري الإسباني', 'fr': 'La Liga', 'es': 'La Liga'}, 'date': '2026-08-23', 'time': '19:30 UTC', 'angle': 9},
]

def slugify(value):
    normalized = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r'[^a-z0-9]+', '-', normalized).strip('-')


def fetch_dynamic_fixtures():
    leagues = [
        ('eng.1', 'Premier League', 'الدوري الإنجليزي الممتاز'),
        ('esp.1', 'La Liga', 'الدوري الإسباني'),
        ('uefa.champions', 'UEFA Champions League', 'دوري أبطال أوروبا'),
    ]
    today = datetime.now(timezone.utc).date()
    found = []
    for day in (today, today + timedelta(days=1)):
        for code, league_en, league_ar in leagues:
            url = f'https://site.api.espn.com/apis/site/v2/sports/soccer/{code}/scoreboard?dates={day.strftime("%Y%m%d")}'
            try:
                with urllib.request.urlopen(url, timeout=15) as response:
                    payload = json.load(response)
            except Exception as exc:
                print(f'warning: ESPN article fixture fetch failed for {code}: {exc}')
                continue
            for event in payload.get('events', []):
                competition = event.get('competitions', [{}])[0]
                competitors = competition.get('competitors', [])
                home = next((item for item in competitors if item.get('homeAway') == 'home'), competitors[0] if competitors else {})
                away = next((item for item in competitors if item.get('homeAway') == 'away'), competitors[1] if len(competitors) > 1 else {})
                status_name = competition.get('status', {}).get('type', {}).get('name', '')
                if status_name in {'STATUS_FULL_TIME', 'STATUS_FINAL'}:
                    continue
                home_name = home.get('team', {}).get('displayName')
                away_name = away.get('team', {}).get('displayName')
                if not home_name or not away_name:
                    continue
                start = event.get('date', '')
                start_time = start[11:16] if len(start) >= 16 else '--:--'
                found.append({'slug': slugify(f'{home_name}-{away_name}'), 'home': home_name, 'away': away_name, 'league': {'en': league_en, 'ar': league_ar, 'fr': league_en, 'es': league_en}, 'date': day.isoformat(), 'time': f'{start_time} UTC', 'angle': len(found) % 10})
    unique = []
    seen = set()
    for fixture in found:
        if fixture['slug'] not in seen:
            unique.append(fixture)
            seen.add(fixture['slug'])
    return unique[:10]


try:
    live_fixtures = fetch_dynamic_fixtures()
    if len(live_fixtures) >= 5:
        fixtures = live_fixtures
except Exception as exc:
    print(f'warning: dynamic fixture generation failed: {exc}')

copy = {
'en': {'dir':'ltr','back':'Back to GlobalScore','tag':'MATCH PREVIEW','read':'6 min read','date_label':'Match date','time_label':'Kick-off','league_label':'Competition','focus':'What to watch','questions':'Three questions before kick-off','details':'Live match details','details_text':'When the match starts, GlobalScore will update the score, minute, events, lineups, referee and venue details from the available live data source.','source':'Fixture and live data: ESPN scoreboard.','home_label':'Home','away_label':'Away','cta':'Open the live scoreboard','seo':'match preview, live score, lineups, referee, stadium, football news'},
'ar': {'dir':'rtl','back':'العودة إلى GlobalScore','tag':'معاينة المباراة','read':'6 دقائق للقراءة','date_label':'تاريخ المباراة','time_label':'موعد البداية','league_label':'المسابقة','focus':'ما الذي يستحق المتابعة؟','questions':'ثلاثة أسئلة قبل البداية','details':'تفاصيل المباراة المباشرة','details_text':'عند انطلاق المباراة، سيحدّث GlobalScore النتيجة والدقيقة والأحداث والتشكيلات والحكم والملعب وفق البيانات الحية المتاحة.','source':'بيانات الموعد والبث المباشر: لوحة نتائج ESPN.','home_label':'صاحب الأرض','away_label':'الضيف','cta':'فتح لوحة النتائج المباشرة','seo':'معاينة المباراة، نتيجة مباشرة، التشكيلة، الحكم، الملعب، أخبار كرة القدم'},
'fr': {'dir':'ltr','back':'Retour à GlobalScore','tag':'AVANT-MATCH','read':'6 min de lecture','date_label':'Date du match','time_label':'Coup d’envoi','league_label':'Compétition','focus':'Le point à surveiller','questions':'Trois questions avant le coup d’envoi','details':'Détails du match en direct','details_text':'Au coup d’envoi, GlobalScore mettra à jour le score, la minute, les événements, les compositions, l’arbitre et le stade selon les données disponibles.','source':'Données du calendrier et du direct : tableau des scores ESPN.','home_label':'Domicile','away_label':'Extérieur','cta':'Ouvrir le tableau des scores','seo':'avant-match, score en direct, compositions, arbitre, stade, actualité football'},
'es': {'dir':'ltr','back':'Volver a GlobalScore','tag':'PREVIA DEL PARTIDO','read':'6 min de lectura','date_label':'Fecha del partido','time_label':'Inicio','league_label':'Competición','focus':'La clave del partido','questions':'Tres preguntas antes del inicio','details':'Detalles del partido en directo','details_text':'Cuando comience el partido, GlobalScore actualizará el marcador, el minuto, los eventos, las alineaciones, el árbitro y el estadio según los datos disponibles.','source':'Datos del calendario y directo: marcador de ESPN.','home_label':'Local','away_label':'Visitante','cta':'Abrir el marcador en directo','seo':'previa del partido, resultado en directo, alineaciones, árbitro, estadio, noticias de fútbol'},
}

angles = {
'en': [
    'The first phase will matter: both sides need a clear rhythm before the match can open up.',
    'The central areas should shape the tempo, especially when possession changes hands.',
    'Transitions may decide the most important moments, with each team looking for space behind the first line.',
    'The defensive test is as interesting as the attacking promise: patience and distances will be decisive.',
    'Set pieces and second balls offer a practical route to momentum in a fixture where small details can count.',
    'The meeting is a useful early test of control, pressing and the ability to protect a lead.',
    'The spotlight will be on how the favourite manages territory while the challenger searches for moments to break forward.',
    'This is the kind of fixture where intensity, rest defence and decision-making can change the story quickly.',
    'The tactical contrast should make the contest compelling, with structure facing movement and variation.',
    'The match brings a clear question of balance: how much risk can each side take without losing control?',
],
'ar': [
    'ستكون المرحلة الأولى مهمة؛ إذ يحتاج الطرفان إلى إيقاع واضح قبل أن تنفتح المباراة.',
    'قد تحدد مناطق الوسط سرعة اللعب، خصوصاً عند انتقال الاستحواذ من فريق إلى آخر.',
    'يمكن أن تحسم التحولات أهم اللحظات، مع بحث كل فريق عن المساحات خلف خط الضغط الأول.',
    'الاختبار الدفاعي لا يقل أهمية عن الوعود الهجومية؛ فالصبر والمسافات قد يصنعان الفارق.',
    'تمنح الكرات الثابتة والكرات الثانية طريقاً عملياً لصناعة الزخم في مباراة قد تحسمها التفاصيل.',
    'تمثل المواجهة اختباراً مبكراً للسيطرة والضغط والقدرة على حماية التقدم.',
    'سيتركز الاهتمام على طريقة إدارة الفريق المرشح للمساحات، وعلى فرص المنافس في الخروج للأمام.',
    'هذه مواجهة قد تغيّر تفاصيلها القصة بسرعة، خصوصاً مع ارتفاع الإيقاع وجودة القرارات.',
    'يوحي اللقاء بتباين تكتيكي جذاب، بين التنظيم والحركة وتغيير مراكز اللعب.',
    'تطرح المباراة سؤالاً واضحاً حول التوازن: كم من المخاطرة يستطيع كل فريق تحملها دون فقدان السيطرة؟',
],
'fr': [
    'La première phase sera importante : les deux équipes devront trouver leur rythme avant que le match ne s’ouvre.',
    'Les zones centrales devraient déterminer le tempo, surtout lors des changements de possession.',
    'Les transitions peuvent décider des moments clés, chaque équipe cherchant l’espace derrière le premier rideau.',
    'Le test défensif est aussi intéressant que la promesse offensive : patience et distances seront essentielles.',
    'Les coups de pied arrêtés et les seconds ballons peuvent créer l’élan dans un match décidé par les détails.',
    'Cette rencontre sera un premier test du contrôle, du pressing et de la capacité à protéger un avantage.',
    'L’attention se portera sur la gestion du territoire par le favori et les sorties rapides de son adversaire.',
    'C’est le type de match où l’intensité et la qualité des décisions peuvent changer le scénario très vite.',
    'Le contraste tactique devrait rendre le duel intéressant, entre structure, mouvement et variations.',
    'La rencontre pose une question d’équilibre : quel risque chaque équipe peut-elle prendre sans perdre le contrôle ?',
],
'es': [
    'La primera fase será importante: ambos equipos necesitarán encontrar su ritmo antes de que el partido se abra.',
    'Las zonas centrales pueden marcar el ritmo, especialmente cuando cambia la posesión.',
    'Las transiciones pueden decidir los momentos clave, con ambos equipos buscando espacios detrás de la primera línea.',
    'El examen defensivo es tan interesante como la promesa ofensiva: la paciencia y las distancias serán decisivas.',
    'Las acciones a balón parado y las segundas jugadas ofrecen una vía práctica para ganar impulso.',
    'El encuentro será una prueba temprana de control, presión y capacidad para proteger una ventaja.',
    'La atención estará en cómo el favorito gestiona el territorio y cómo el rival encuentra salidas hacia adelante.',
    'Es un partido en el que la intensidad y la toma de decisiones pueden cambiar la historia rápidamente.',
    'El contraste táctico promete un duelo atractivo entre estructura, movimiento y variación.',
    'El partido plantea una pregunta de equilibrio: ¿cuánto riesgo puede asumir cada equipo sin perder el control?',
],
}

section_intro = {
'en': lambda f: f"{f['home']} and {f['away']} meet in the {f['league']['en']} on {f['date']}. The fixture is part of the football schedule for today and tomorrow, and this briefing focuses on the match context without inventing line-ups or confirmed player news.",
'ar': lambda f: f"يلتقي {f['home']} و{f['away']} في {f['league']['ar']} يوم {f['date']}. تأتي المواجهة ضمن برنامج مباريات اليوم والغد، وتركز هذه المعاينة على سياق اللقاء دون اختلاق تشكيلات أو أخبار مؤكدة عن اللاعبين.",
'fr': lambda f: f"{f['home']} et {f['away']} se retrouvent en {f['league']['fr']} le {f['date']}. Cette affiche figure au programme du jour et du lendemain ; cette analyse présente le contexte sans inventer de compositions ni d’informations confirmées sur les joueurs.",
'es': lambda f: f"{f['home']} y {f['away']} se enfrentan en {f['league']['es']} el {f['date']}. El partido forma parte del calendario de hoy y mañana, y esta previa analiza el contexto sin inventar alineaciones ni noticias confirmadas de los jugadores.",
}

question_text = {
'en': ['Who controls the first pass after winning the ball?', 'Can either side turn territorial pressure into clear chances?', 'Which team adapts better if the opening plan stops working?'],
'ar': ['من يسيطر على التمريرة الأولى بعد استعادة الكرة؟', 'هل يستطيع أي طرف تحويل الضغط الميداني إلى فرص واضحة؟', 'أي فريق سيتكيف بشكل أفضل إذا لم تنجح الخطة الأولى؟'],
'fr': ['Qui contrôlera la première passe après la récupération ?', 'Une équipe peut-elle transformer sa pression territoriale en occasions nettes ?', 'Qui s’adaptera le mieux si le plan initial ne fonctionne pas ?'],
'es': ['¿Quién controlará el primer pase tras recuperar el balón?', '¿Puede alguno convertir la presión territorial en ocasiones claras?', '¿Qué equipo se adaptará mejor si el plan inicial deja de funcionar?'],
}


def page_for(fixture, lang):
    c = copy[lang]
    slug = fixture['slug']
    title_map = {
        'en': f"{fixture['home']} vs {fixture['away']}: match preview, time and key questions",
        'ar': f"معاينة مباراة {fixture['home']} و{fixture['away']}: الموعد وأبرز الأسئلة",
        'fr': f"{fixture['home']} - {fixture['away']} : avant-match, horaire et enjeux",
        'es': f"{fixture['home']} - {fixture['away']}: previa, horario y claves",
    }
    title = title_map[lang]
    description = section_intro[lang](fixture)
    canonical = f'{BASE}/{lang}/articles/{slug}.html'
    hreflang = '\n'.join(f'<link rel="alternate" hreflang="{code}" href="{BASE}/{code}/articles/{slug}.html">' for code in copy)
    questions = ''.join(f'<li>{escape(q)}</li>' for q in question_text[lang])
    home, away = escape(fixture['home']), escape(fixture['away'])
    league = escape(fixture['league'][lang])
    paragraphs = [description, angles[lang][fixture['angle']], c['details_text']]
    body = ''.join(f'<p>{escape(p)}</p>' for p in paragraphs)
    table = f'''<div class="article-fact-grid"><div><small>{c['home_label']}</small><strong>{home}</strong></div><div><small>{c['away_label']}</small><strong>{away}</strong></div><div><small>{c['league_label']}</small><strong>{league}</strong></div><div><small>{c['date_label']}</small><strong>{escape(fixture['date'])}</strong></div><div><small>{c['time_label']}</small><strong>{escape(fixture['time'])}</strong></div></div>'''
    return f'''<!doctype html>
<html lang="{lang}" dir="{c['dir']}" prefix="og: https://ogp.me/ns#">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} | GlobalScore</title>
<meta name="description" content="{escape(description)}"><meta name="keywords" content="{escape(c['seo'])}">
<link rel="canonical" href="{canonical}">
{hreflang}
<link rel="stylesheet" href="../../assets/css/critical.css?v=4"><link rel="stylesheet" href="../../assets/css/main.css?v=5">
<meta property="og:type" content="article"><meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(description)}"><meta property="og:url" content="{canonical}">
<script type="application/ld+json">{__import__('json').dumps({'@context':'https://schema.org','@type':'Article','headline':title,'description':description,'datePublished':fixture['date'],'dateModified':datetime.now(timezone.utc).date().isoformat(),'author':{'@type':'Organization','name':'GlobalScore Editorial'},'publisher':{'@type':'Organization','name':'GlobalScore'},'mainEntityOfPage':{'@type':'WebPage','@id':canonical},'isAccessibleForFree':True}, ensure_ascii=False)}</script>
</head>
<body><header class="site-header"><div class="header-container"><a class="brand" href="../../{lang}/"><img class="logo-img" src="../../assets/img/logo.svg" alt=""><span>Global<span class="brand-accent">Score</span></span></a><nav class="nav"><a class="nav-link" href="../../{lang}/">{c['back']}</a></nav><div class="controls"><a class="language-btn" href="../../ar/articles/{slug}.html">AR</a><a class="language-btn" href="../../en/articles/{slug}.html">EN</a><a class="language-btn" href="../../fr/articles/{slug}.html">FR</a><a class="language-btn" href="../../es/articles/{slug}.html">ES</a></div></div></header>
<main class="page-shell"><article class="article-page"><header class="article-header"><a class="article-back" href="../../{lang}/">← {c['back']}</a><span class="section-kicker">{c['tag']}</span><h1>{escape(title)}</h1><p class="article-dek">{escape(description)}</p><div class="article-meta"><span>{c['read']}</span><span>{escape(fixture['date'])}</span><span>GlobalScore Editorial</span></div></header><div class="article-content">{table}<h2>{c['focus']}</h2>{body}<h2>{c['questions']}</h2><ol>{questions}</ol><h2>{c['details']}</h2><p>{escape(c['details_text'])}</p><p class="article-note">{escape(c['source'])}</p><p><a class="primary-btn" href="../../{lang}/#today">{c['cta']} <span>→</span></a></p></div></article></main><footer class="footer"><div class="footer-inner"><a class="brand footer-brand" href="../../{lang}/"><img src="../../assets/img/logo.svg" alt=""><span>Global<span class="brand-accent">Score</span></span></a><p>GlobalScore Editorial</p><div class="footer-links"><a href="../../ar/articles/{slug}.html">العربية</a><a href="../../en/articles/{slug}.html">English</a><a href="../../fr/articles/{slug}.html">Français</a><a href="../../es/articles/{slug}.html">Español</a></div></div></footer></body></html>'''


def landing(lang):
    c = copy[lang]
    headings = {'en':'Football previews for today and tomorrow','ar':'معاينات مباريات اليوم والغد','fr':'Avant-matchs du jour et du lendemain','es':'Previas de los partidos de hoy y mañana'}
    intro = {'en':'Original, source-aware match briefings with clear times and live-data links.', 'ar':'معاينات أصلية للمباريات مع المواعيد وروابط البيانات الحية.', 'fr':'Des avant-matchs originaux avec horaires clairs et liens vers les données en direct.', 'es':'Previas originales con horarios claros y enlaces a los datos en directo.'}
    cards = ''.join(f'<a class="news-card" href="articles/{f["slug"]}.html"><div class="news-meta"><span class="news-tag">{escape(c["tag"])}</span><span>{escape(f["date"])}</span></div><h2>{escape(f["home"] + " – " + f["away"])}</h2><p>{escape(f["league"][lang])} · {escape(f["time"])}</p><span class="news-arrow">→</span></a>' for f in fixtures)
    return f'''<!doctype html><html lang="{lang}" dir="{c['dir']}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>GlobalScore | {headings[lang]}</title><meta name="description" content="{intro[lang]}"><link rel="canonical" href="{BASE}/{lang}/"><link rel="alternate" hreflang="ar" href="{BASE}/ar/"><link rel="alternate" hreflang="en" href="{BASE}/en/"><link rel="alternate" hreflang="fr" href="{BASE}/fr/"><link rel="alternate" hreflang="es" href="{BASE}/es/"><link rel="stylesheet" href="../assets/css/critical.css?v=4"><link rel="stylesheet" href="../assets/css/main.css?v=5"></head><body><header class="site-header"><div class="header-container"><a class="brand" href="../{lang}/"><img class="logo-img" src="../assets/img/logo.svg" alt=""><span>Global<span class="brand-accent">Score</span></span></a><div class="controls"><a class="language-btn" href="../ar/">AR</a><a class="language-btn" href="../en/">EN</a><a class="language-btn" href="../fr/">FR</a><a class="language-btn" href="../es/">ES</a></div></div></header><main class="page-shell"><section class="hero-panel"><div class="hero-copy"><span class="eyebrow">GLOBAL SCORE EDITORIAL</span><h1>{headings[lang]}</h1><p>{intro[lang]}</p></div></section><section class="content-section"><div class="section-heading"><div><span class="section-kicker">{c['tag']}</span><h2>{headings[lang]}</h2></div></div><div class="news-grid">{cards}</div></section></main><footer class="footer"><div class="footer-inner"><a class="brand footer-brand" href="../{lang}/"><img src="../assets/img/logo.svg" alt=""><span>Global<span class="brand-accent">Score</span></span></a><div class="footer-links"><a href="../ar/">العربية</a><a href="../en/">English</a><a href="../fr/">Français</a><a href="../es/">Español</a></div></div></footer></body></html>'''

for lang in copy:
    (ROOT / lang / 'articles').mkdir(parents=True, exist_ok=True)
    for fixture in fixtures:
        (ROOT / lang / 'articles' / f"{fixture['slug']}.html").write_text(page_for(fixture, lang), encoding='utf-8')
    (ROOT / lang / 'articles' / 'index.html').write_text(landing(lang), encoding='utf-8')
    if lang in {'fr', 'es'}:
        (ROOT / lang / 'index.html').write_text(landing(lang), encoding='utf-8')

urls = [f'{BASE}/{lang}/' for lang in copy]
urls += [f'{BASE}/{lang}/articles/' for lang in copy]
urls += [f'{BASE}/{lang}/articles/{fixture["slug"]}.html' for lang in copy for fixture in fixtures]
sitemap_path = ROOT / 'Sitemap.xml'
existing_sitemap = sitemap_path.read_text(encoding='utf-8') if sitemap_path.exists() else ''
existing_urls = set(re.findall(r'<loc>(.*?)</loc>', existing_sitemap))
all_urls = sorted(existing_urls | set(urls))
lastmod = datetime.now(timezone.utc).date().isoformat()
xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
xml += [f'  <url><loc>{url}</loc><lastmod>{lastmod}</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>' for url in all_urls]
xml.append('</urlset>')
sitemap_path.write_text('\n'.join(xml) + '\n', encoding='utf-8')
shutil.copyfile(sitemap_path, ROOT / 'sitemap.xml')

print(f'generated {len(fixtures)} articles in {len(copy)} languages ({len(fixtures) * len(copy)} pages)')
print(f'sitemap URLs: {len(all_urls)}')
