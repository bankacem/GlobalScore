from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path
import json
import os
import re
import shutil
import unicodedata
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://bankacem.github.io/GlobalScore'
LANGS = ('ar', 'en', 'fr', 'es')
TEMPLATE_VERSION = '2026-08-editorial-v2'
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
    excluded = {'STATUS_FULL_TIME', 'STATUS_FINAL', 'STATUS_IN_PROGRESS', 'STATUS_HALFTIME', 'STATUS_END_PERIOD', 'STATUS_POSTPONED', 'STATUS_CANCELED', 'STATUS_CANCELLED'}
    if status_name in excluded:
        return None
    home_name = home.get('team', {}).get('displayName')
    away_name = away.get('team', {}).get('displayName')
    if not home_name or not away_name:
        return None
    start = event.get('date', '')
    start_time = start[11:16] if len(start) >= 16 else '--:--'
    slug = f'{day.isoformat()}-{slugify(home_name)}-{slugify(away_name)}'
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
    league_map.update({item[2]: item for item in LEAGUES})
    for item in candidates:
        if str(item.get('status', '')).upper() in {'FT', 'FINAL', 'FINISHED', 'CANCELLED', 'CANCELED', 'POSTPONED'}:
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
        raw_id = item.get('id') or f'{match_day.isoformat()}:{slugify(home)}:{slugify(away)}'
        match_key = f'snapshot:{raw_id}'
        if match_key in seen:
            continue
        seen.add(match_key)
        result.append({'event_id': str(item.get('id') or ''), 'match_key': match_key, 'slug': f'{match_day.isoformat()}-{slugify(home)}-{slugify(away)}', 'home': home, 'away': away, 'league': {'en': league[1], 'ar': league[2], 'fr': league[3], 'es': league[4]}, 'league_code': league[0], 'date': match_day.isoformat(), 'time': f"{item.get('time') or '--:--'} UTC", 'angle': len(result) % 10})
    return result[:10]


FALLBACK_FIXTURES = [
    {'event_id': '', 'match_key': 'fallback:hull-city:manchester-united', 'slug': '2026-08-22-hull-city-manchester-united', 'home': 'Hull City', 'away': 'Manchester United', 'league': {'en': 'Premier League', 'ar': 'الدوري الإنجليزي الممتاز', 'fr': 'Premier League', 'es': 'Premier League'}, 'league_code': 'eng.1', 'date': '2026-08-22', 'time': '11:30 UTC', 'angle': 0},
    {'event_id': '', 'match_key': 'fallback:everton:crystal-palace', 'slug': '2026-08-22-everton-crystal-palace', 'home': 'Everton', 'away': 'Crystal Palace', 'league': {'en': 'Premier League', 'ar': 'الدوري الإنجليزي الممتاز', 'fr': 'Premier League', 'es': 'Premier League'}, 'league_code': 'eng.1', 'date': '2026-08-22', 'time': '14:00 UTC', 'angle': 1},
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
    'en': {'dir': 'ltr', 'back': 'Back to GlobalScore', 'tag': 'MATCH PREVIEW', 'read': '5 min read', 'questions': 'Three questions before kick-off', 'home': 'Home', 'away': 'Away', 'league': 'Competition', 'date': 'Match date', 'time': 'Kick-off', 'follow': 'How to follow the match', 'confirmed': 'What is confirmed — and what is not', 'sources': 'Sources and editorial note', 'cta': 'Open the live score and match details', 'index': 'Browse all match previews', 'table': 'View live standings and league coverage', 'source_link': 'Open the competition source'},
    'ar': {'dir': 'rtl', 'back': 'العودة إلى GlobalScore', 'tag': 'معاينة المباراة', 'read': '5 دقائق للقراءة', 'questions': 'ثلاثة أسئلة قبل البداية', 'home': 'صاحب الأرض', 'away': 'الضيف', 'league': 'المسابقة', 'date': 'تاريخ المباراة', 'time': 'موعد البداية', 'follow': 'كيف تتابع المباراة؟', 'confirmed': 'ما نعرفه وما لم يتأكد بعد', 'sources': 'المصادر والمنهج التحريري', 'cta': 'فتح النتيجة المباشرة وتفاصيل المباراة', 'index': 'تصفح كل معاينات المباريات', 'table': 'عرض الترتيب المباشر وتغطية المسابقة', 'source_link': 'فتح مصدر المسابقة'},
    'fr': {'dir': 'ltr', 'back': 'Retour à GlobalScore', 'tag': 'AVANT-MATCH', 'read': '5 min de lecture', 'questions': 'Trois questions avant le coup d’envoi', 'home': 'Domicile', 'away': 'Extérieur', 'league': 'Compétition', 'date': 'Date du match', 'time': 'Coup d’envoi', 'follow': 'Comment suivre le match', 'confirmed': 'Ce qui est confirmé — et ce qui ne l’est pas', 'sources': 'Sources et méthode éditoriale', 'cta': 'Ouvrir le score en direct et les détails', 'index': 'Parcourir toutes les avant-matchs', 'table': 'Voir le classement et la couverture', 'source_link': 'Ouvrir la source de la compétition'},
    'es': {'dir': 'ltr', 'back': 'Volver a GlobalScore', 'tag': 'PREVIA DEL PARTIDO', 'read': '5 min de lectura', 'questions': 'Tres preguntas antes del inicio', 'home': 'Local', 'away': 'Visitante', 'league': 'Competición', 'date': 'Fecha del partido', 'time': 'Inicio', 'follow': 'Cómo seguir el partido', 'confirmed': 'Qué está confirmado y qué no', 'sources': 'Fuentes y método editorial', 'cta': 'Abrir el marcador en directo y los detalles', 'index': 'Ver todas las previas de GlobalScore', 'table': 'Ver la clasificación y la cobertura', 'source_link': 'Abrir la fuente de la competición'},
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

CONTEXT = {
    'en': 'This preview begins with information a reader can use: the competition, the fixture, the date and the published kick-off time. It then adds a tactical reading that is deliberately careful about evidence. A probable line-up, an unconfirmed injury or a prediction is not presented as a fact.',
    'ar': 'تبدأ هذه المعاينة بالمعلومات التي يستطيع القارئ الاستفادة منها: المسابقة، طرفا اللقاء، التاريخ وموعد البداية المعلن. ثم تضيف قراءة تكتيكية تحافظ على الدقة؛ فلا تُعرض التشكيلة المتوقعة أو الإصابة غير المؤكدة أو التوقع على أنها حقيقة.',
    'fr': 'Cette avant-match commence par les informations utiles : la compétition, l’affiche, la date et l’horaire annoncé. Elle ajoute ensuite une lecture tactique prudente. Une composition probable, une blessure non confirmée ou une prédiction ne sont pas présentées comme des faits.',
    'es': 'Esta previa comienza con la información útil: la competición, el encuentro, la fecha y el horario anunciado. Después añade una lectura táctica prudente. Una alineación probable, una lesión no confirmada o una predicción no se presentan como hechos.',
}

METHOD = {
    'en': 'GlobalScore separates scheduled information from match-day information. Starting line-ups, referee assignments, live events and final statistics are added only when the available data source publishes them. Until then, the useful question is not who will definitely start, but which behaviours could shape the match.',
    'ar': 'يفصل GlobalScore بين معلومات الجدول ومعلومات يوم المباراة. ولا تُضاف التشكيلات الأساسية أو الحكم أو الأحداث الحية أو الإحصاءات النهائية إلا عند نشرها في مصدر البيانات المتاح. وحتى ذلك الحين، يكون السؤال المفيد هو السلوكيات التي قد تشكل اللقاء، لا من سيبدأ بشكل مؤكد.',
    'fr': 'GlobalScore sépare les données du calendrier des informations du jour du match. Les compositions, l’arbitre, les événements et les statistiques finales ne sont ajoutés qu’après leur publication dans la source disponible. Avant cela, l’enjeu consiste à observer les comportements susceptibles de structurer le duel.',
    'es': 'GlobalScore separa los datos del calendario de la información del día de partido. Las alineaciones, el árbitro, los acontecimientos y las estadísticas finales solo se añaden cuando aparecen en la fuente disponible. Hasta entonces, lo útil es observar los comportamientos que pueden estructurar el duelo.',
}

LENS = {
    'en': 'The central lens is the moment possession changes hands. The first pass after a recovery can decide whether a side attacks an organised defence or faces a transition. Width, support around the ball and the distance between midfield and defence are therefore more useful clues than a simple favourite-versus-underdog label.',
    'ar': 'تتمثل الزاوية الرئيسية في لحظة انتقال الاستحواذ. فقد تحدد التمريرة الأولى بعد استعادة الكرة ما إذا كان الفريق سيهاجم دفاعاً منظماً أم سيواجه تحولاً سريعاً. لذلك تبدو متابعة العرض والدعم حول حامل الكرة والمسافة بين الوسط والدفاع أكثر فائدة من وصف مبسط مثل المرشح والمنافس.',
    'fr': 'La lecture centrale se situe au moment où la possession change de camp. La première passe après une récupération peut décider si une équipe attaque un bloc organisé ou s’expose à une transition. La largeur, le soutien autour du porteur et les distances entre les lignes sont donc plus révélateurs qu’une simple opposition favori-outsider.',
    'es': 'La clave está en el momento en que cambia la posesión. El primer pase tras recuperar el balón puede decidir si un equipo ataca una defensa organizada o se expone a una transición. La amplitud, el apoyo alrededor del poseedor y la distancia entre líneas ofrecen más pistas que una simple etiqueta de favorito y rival.',
}

WATCH = {
    'en': ['The first pass after a turnover: can either side play forward without exposing the centre?', 'The wide areas: which team creates a two-versus-one or reaches the byline more consistently?', 'Set pieces and second balls: small moments that can change territory and momentum.', 'The reaction to pressure: whether the team without the ball stays compact instead of chasing individually.'],
    'ar': ['التمريرة الأولى بعد فقدان الكرة أو استعادتها: هل يستطيع أحد الطرفين التقدم دون كشف العمق؟', 'الأطراف: أي فريق يخلق زيادة عددية أو يصل إلى خط المرمى باستمرار؟', 'الكرات الثابتة والكرات الثانية: تفاصيل صغيرة قد تغير مناطق اللعب والزخم.', 'رد الفعل تحت الضغط: هل يحافظ الفريق دون كرة على تماسكه بدلاً من المطاردة الفردية؟'],
    'fr': ['La première passe après une récupération : une équipe peut-elle avancer sans exposer l’axe ?', 'Les couloirs : qui crée le plus régulièrement une supériorité ou atteint la ligne de fond ?', 'Les coups de pied arrêtés et les deuxièmes ballons, capables de modifier le territoire et le rythme.', 'La réaction au pressing : l’équipe sans ballon reste-t-elle compacte au lieu de défendre individuellement ?'],
    'es': ['El primer pase tras recuperar el balón: ¿puede algún equipo avanzar sin dejar expuesto el centro?', 'Las bandas: ¿quién crea superioridades o llega a la línea de fondo con más continuidad?', 'Las jugadas a balón parado y las segundas acciones, capaces de cambiar el territorio y el ritmo.', 'La reacción a la presión: ¿el equipo sin balón mantiene la estructura en lugar de perseguir de forma individual?'],
}

COMPETITION_LINKS = {'eng.1': 'https://www.premierleague.com/en/', 'esp.1': 'https://www.laliga.com/en-GB', 'uefa.champions': 'https://www.uefa.com/uefachampionsleague/', 'egy.1': 'https://www.espn.com/soccer/scoreboard/_/league/egy.1'}


def page_for(fixture, lang):
    c = COPY[lang]
    slug = fixture['slug']
    title = {'en': f"{fixture['home']} vs {fixture['away']}: preview, kick-off time and key questions", 'ar': f"معاينة مباراة {fixture['home']} و{fixture['away']}: الموعد وأهم الأسئلة", 'fr': f"{fixture['home']} - {fixture['away']} : avant-match, horaire et enjeux", 'es': f"{fixture['home']} - {fixture['away']}: previa, horario y claves"}[lang]
    description = {'en': f"{fixture['home']} vs {fixture['away']} in the {fixture['league']['en']}: match time, tactical questions and live-score links for {fixture['date']}.", 'ar': f"معاينة مباراة {fixture['home']} و{fixture['away']} في {fixture['league']['ar']}: الموعد والأسئلة التكتيكية وروابط المتابعة المباشرة يوم {fixture['date']}.", 'fr': f"{fixture['home']} contre {fixture['away']} en {fixture['league']['fr']} : horaire, clés tactiques et liens vers le direct le {fixture['date']}.", 'es': f"{fixture['home']} contra {fixture['away']} en {fixture['league']['es']}: horario, claves tácticas y enlaces al directo del {fixture['date']}."}[lang]
    canonical = f'{BASE}/{lang}/articles/{slug}.html'
    hreflang = '\n'.join(f'<link rel="alternate" hreflang="{code}" href="{BASE}/{code}/articles/{slug}.html">' for code in LANGS)
    facts = f'<div class="article-fact-grid"><div><small>{c["home"]}</small><strong>{escape(fixture["home"])}</strong></div><div><small>{c["away"]}</small><strong>{escape(fixture["away"])}</strong></div><div><small>{c["league"]}</small><strong>{escape(fixture["league"][lang])}</strong></div><div><small>{c["date"]}</small><strong>{escape(fixture["date"])}</strong></div><div><small>{c["time"]}</small><strong>{escape(fixture["time"])}</strong></div></div>'
    questions = ''.join(f'<li>{escape(item)}</li>' for item in QUESTIONS[lang])
    watch_items = ''.join(f'<li>{escape(item)}</li>' for item in WATCH[lang])
    internal_score = f'../../{lang}/#today'
    internal_index = f'../../{lang}/articles/'
    internal_table = f'../../{lang}/#leagues'
    external_source = COMPETITION_LINKS.get(fixture['league_code'], 'https://www.espn.com/soccer/scoreboard')
    lens_heading = {'en': 'The analytical lens', 'ar': 'الزاوية التحليلية', 'fr': 'La lecture analytique', 'es': 'La clave del análisis'}[lang]
    watch_heading = {'en': 'What to watch before kick-off', 'ar': 'ما الذي يستحق المتابعة قبل البداية؟', 'fr': 'Les points à surveiller avant le coup d’envoi', 'es': 'Qué observar antes del inicio'}[lang]
    follow_text = {'en': f'Use the live scoreboard for the score, minute, events and confirmed line-ups when they become available. Return to the {fixture["league"][lang]} coverage on GlobalScore for standings and related previews.', 'ar': f'استخدم لوحة النتائج المباشرة لمتابعة النتيجة والدقيقة والأحداث والتشكيلات المؤكدة عند ظهورها. ويمكنك العودة إلى تغطية {fixture["league"][lang]} على GlobalScore لمتابعة الترتيب والمعاينات ذات الصلة.', 'fr': f'Consultez le tableau des scores pour le résultat, la minute, les événements et les compositions confirmées. La couverture de {fixture["league"][lang]} sur GlobalScore permet aussi de retrouver le classement et les avant-matchs associés.', 'es': f'Consulta el marcador en directo para ver el resultado, el minuto, los acontecimientos y las alineaciones confirmadas. La cobertura de {fixture["league"][lang]} en GlobalScore también reúne la clasificación y las previas relacionadas.'}[lang]
    source_text = {'en': 'Fixture timing and live match fields are checked against the available ESPN scoreboard feed. The competition link below provides official context. GlobalScore adds its own editorial analysis and does not reproduce third-party articles.', 'ar': 'تمت مراجعة موعد المباراة وحقولها الحية مقابل موجز ESPN المتاح. وُضع رابط المسابقة أدناه للوصول إلى السياق الرسمي، بينما يضيف GlobalScore تحليله التحريري الخاص ولا ينسخ مقالات الأطراف الأخرى.', 'fr': 'L’horaire et les champs du direct sont comparés au flux ESPN disponible. Le lien de la compétition apporte le contexte officiel. GlobalScore ajoute sa propre analyse et ne reproduit pas les articles de tiers.', 'es': 'El horario y los campos del directo se contrastan con el marcador de ESPN disponible. El enlace de la competición aporta el contexto oficial. GlobalScore añade su propio análisis y no reproduce artículos de terceros.'}[lang]
    body = f'<p>{escape(CONTEXT[lang])}</p><p>{escape(METHOD[lang])}</p><h2>{escape(lens_heading)}</h2><p>{escape(LENS[lang])}</p><p>{escape(ANGLES[lang][fixture["angle"] % len(ANGLES[lang])])}</p><h2>{escape(watch_heading)}</h2><ul class="article-checklist">{watch_items}</ul><h2>{escape(c["questions"])}</h2><ol>{questions}</ol><h2>{escape(c["follow"])}</h2><p>{escape(follow_text)}</p><nav class="article-links" aria-label="Related GlobalScore links"><a href="{internal_score}">{escape(c["cta"])}</a><a href="{internal_table}">{escape(c["table"])}</a><a href="{internal_index}">{escape(c["index"])}</a></nav><h2>{escape(c["sources"])}</h2><p>{escape(source_text)}</p><p class="article-note"><a href="{escape(external_source)}" rel="noopener noreferrer" target="_blank">{escape(c["source_link"])}</a> · <a href="https://www.espn.com/soccer/scoreboard" rel="noopener noreferrer" target="_blank">ESPN football scoreboard</a></p>'
    schema = json.dumps({'@context': 'https://schema.org', '@type': 'Article', 'headline': title, 'description': description, 'datePublished': f"{fixture['date']}T00:00:00Z", 'dateModified': fixture['date'], 'author': {'@type': 'Organization', 'name': 'GlobalScore Editorial', 'url': BASE}, 'publisher': {'@type': 'Organization', 'name': 'GlobalScore', 'url': BASE}, 'mainEntityOfPage': {'@type': 'WebPage', '@id': canonical}, 'articleSection': fixture['league'][lang], 'isAccessibleForFree': True}, ensure_ascii=False)
    return f'''<!doctype html><html lang="{lang}" dir="{c['dir']}" prefix="og: https://ogp.me/ns#"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)} | GlobalScore</title><meta name="description" content="{escape(description)}"><meta name="robots" content="index,follow"><link rel="canonical" href="{canonical}">{hreflang}<link rel="alternate" hreflang="x-default" href="{BASE}/en/articles/{slug}.html"><link rel="stylesheet" href="../../assets/css/critical.css?v=4"><link rel="stylesheet" href="../../assets/css/main.css?v=8"><meta property="og:type" content="article"><meta property="og:site_name" content="GlobalScore"><meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(description)}"><meta property="og:url" content="{canonical}"><meta property="article:published_time" content="{fixture['date']}T00:00:00Z"><meta property="article:section" content="{escape(fixture['league'][lang])}"><meta name="twitter:card" content="summary"><script type="application/ld+json">{schema}</script></head><body><header class="site-header"><div class="header-container"><a class="brand" href="../../{lang}/"><img class="logo-img" src="../../assets/img/logo.svg" alt=""><span>Global<span class="brand-accent">Score</span></span></a><nav class="nav"><a class="nav-link" href="../../{lang}/">{c['back']}</a><a class="nav-link" href="{internal_index}">{escape(c['index'])}</a></nav><div class="controls"><a class="language-btn" href="../../ar/articles/{slug}.html">AR</a><a class="language-btn" href="../../en/articles/{slug}.html">EN</a><a class="language-btn" href="../../fr/articles/{slug}.html">FR</a><a class="language-btn" href="../../es/articles/{slug}.html">ES</a></div></div></header><main class="page-shell"><article class="article-page"><header class="article-header"><a class="article-back" href="../../{lang}/">← {c['back']}</a><span class="section-kicker">{c['tag']}</span><h1>{escape(title)}</h1><p class="article-dek">{escape(description)}</p><div class="article-meta"><span>{c['read']}</span><time datetime="{fixture['date']}">{escape(fixture['date'])}</time><span>GlobalScore Editorial</span></div></header><div class="article-content">{facts}{body}<p><a class="primary-btn" href="{internal_score}">{escape(c['cta'])} <span>→</span></a></p></div></article></main><footer class="footer"><div class="footer-inner"><a class="brand footer-brand" href="../../{lang}/"><img class="logo-img" src="../../assets/img/logo.svg" alt=""><span>Global<span class="brand-accent">Score</span></span></a><p>GlobalScore Editorial</p><div class="footer-links"><a href="../../ar/articles/{slug}.html">العربية</a><a href="../../en/articles/{slug}.html">English</a><a href="../../fr/articles/{slug}.html">Français</a><a href="../../es/articles/{slug}.html">Español</a></div></div></footer></body></html>'''


def landing(lang):
    c = COPY[lang]
    headings = {'en': 'Football previews for today and tomorrow', 'ar': 'معاينات مباريات اليوم والغد', 'fr': 'Avant-matchs du jour et du lendemain', 'es': 'Previas de los partidos de hoy y mañana'}
    intro = {'en': 'Original, source-aware match briefings with clear times, tactical questions and live-data links.', 'ar': 'معاينات أصلية للمباريات مع المواعيد والأسئلة التكتيكية وروابط البيانات الحية.', 'fr': 'Des avant-matchs originaux avec horaires clairs, clés tactiques et liens vers le direct.', 'es': 'Previas originales con horarios claros, claves tácticas y enlaces a los datos en directo.'}
    cards = ''.join(f'<a class="news-card" href="{f["slug"]}.html"><div class="news-meta"><span class="news-tag">{escape(c["tag"])}</span><span>{escape(f["date"])}</span></div><h3>{escape(f["home"] + " – " + f["away"])}</h3><p>{escape(f["league"][lang])} · {escape(f["time"])}</p><span class="news-arrow">→</span></a>' for f in fixtures)
    return f'''<!doctype html><html lang="{lang}" dir="{c['dir']}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>GlobalScore | {headings[lang]}</title><meta name="description" content="{intro[lang]}"><link rel="canonical" href="{BASE}/{lang}/articles/"><link rel="alternate" hreflang="ar" href="{BASE}/ar/articles/"><link rel="alternate" hreflang="en" href="{BASE}/en/articles/"><link rel="alternate" hreflang="fr" href="{BASE}/fr/articles/"><link rel="alternate" hreflang="es" href="{BASE}/es/articles/"><link rel="alternate" hreflang="x-default" href="{BASE}/en/articles/"><link rel="stylesheet" href="../../assets/css/critical.css?v=4"><link rel="stylesheet" href="../../assets/css/main.css?v=8"></head><body><header class="site-header"><div class="header-container"><a class="brand" href="../../{lang}/"><img class="logo-img" src="../../assets/img/logo.svg" alt=""><span>Global<span class="brand-accent">Score</span></span></a><div class="controls"><a class="language-btn" href="../../ar/articles/">AR</a><a class="language-btn" href="../../en/articles/">EN</a><a class="language-btn" href="../../fr/articles/">FR</a><a class="language-btn" href="../../es/articles/">ES</a></div></div></header><main class="page-shell"><section class="hero-panel"><div class="hero-copy"><span class="eyebrow">GLOBAL SCORE EDITORIAL</span><h1>{headings[lang]}</h1><p>{intro[lang]}</p></div></section><section class="content-section"><div class="section-heading"><div><span class="section-kicker">{c['tag']}</span><h2>{headings[lang]}</h2></div></div><div class="news-grid">{cards}</div></section></main><footer class="footer"><div class="footer-inner"><a class="brand footer-brand" href="../../{lang}/"><img class="logo-img" src="../../assets/img/logo.svg" alt=""><span>Global<span class="brand-accent">Score</span></span></a><div class="footer-links"><a href="../../ar/">العربية</a><a href="../../en/">English</a><a href="../../fr/">Français</a><a href="../../es/">Español</a></div></div></footer></body></html>'''


registry_path = ROOT / 'assets/data/article_registry.json'
try:
    registry = json.loads(registry_path.read_text(encoding='utf-8')) if registry_path.exists() else {}
except json.JSONDecodeError:
    registry = {}
now = datetime.now(timezone.utc).isoformat()
created_or_updated = 0
skipped_existing = 0
for fixture in fixtures:
    key = fixture['match_key']
    record = registry.get(key, {})
    article_paths = [ROOT / lang / 'articles' / f"{fixture['slug']}.html" for lang in LANGS]
    needs_write = os.getenv('GLOBAL_SCORE_FORCE_ARTICLES') == '1' or record.get('templateVersion') != TEMPLATE_VERSION or not all(path.exists() for path in article_paths)
    if needs_write:
        for lang, article_path in zip(LANGS, article_paths):
            article_path.parent.mkdir(parents=True, exist_ok=True)
            article_path.write_text(page_for(fixture, lang), encoding='utf-8')
        record['lastGenerated'] = now
        created_or_updated += 1
    else:
        skipped_existing += 1
    registry[key] = {'eventId': fixture['event_id'], 'slug': fixture['slug'], 'date': fixture['date'], 'home': fixture['home'], 'away': fixture['away'], 'lastGenerated': record.get('lastGenerated', now), 'languages': list(LANGS), 'templateVersion': TEMPLATE_VERSION}

for lang in LANGS:
    article_dir = ROOT / lang / 'articles'
    article_dir.mkdir(parents=True, exist_ok=True)
    (article_dir / 'index.html').write_text(landing(lang), encoding='utf-8')
registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

sitemap_path = ROOT / 'Sitemap.xml'
existing = sitemap_path.read_text(encoding='utf-8') if sitemap_path.exists() else ''
existing_urls = set(re.findall(r'<loc>(.*?)</loc>', existing))
existing_lastmods = dict(re.findall(r'<loc>(.*?)</loc>\s*<lastmod>(.*?)</lastmod>', existing))
new_urls = {f'{BASE}/{lang}/articles/{fixture["slug"]}.html' for lang in LANGS for fixture in fixtures}
new_urls |= {f'{BASE}/{lang}/articles/' for lang in LANGS}
new_urls |= {f'{BASE}/{lang}/articles/player-watch-odegaard.html' for lang in LANGS}
new_urls |= {f'{BASE}/{lang}/' for lang in LANGS}
all_urls = sorted(existing_urls | new_urls)
today_iso = date.today().isoformat()
xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for url in all_urls:
    lastmod = existing_lastmods.get(url, today_iso)
    xml.append(f'  <url><loc>{escape(url)}</loc><lastmod>{lastmod}</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>')
xml.append('</urlset>')
sitemap_path.write_text('\n'.join(xml) + '\n', encoding='utf-8')
shutil.copyfile(sitemap_path, ROOT / 'sitemap.xml')

print(f'created_or_updated {created_or_updated} fixtures x {len(LANGS)} languages = {created_or_updated * len(LANGS)} pages')
print(f'skipped_existing {skipped_existing} fixtures already registered with complete pages')
print(f'registry records: {len(registry)}')
print(f'sitemap URLs: {len(all_urls)}')
