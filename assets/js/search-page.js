const LANG = window.GLOBAL_LANG || 'en';
const AR = LANG === 'ar';
const copy = {
  en: { noResults: 'No matching results yet.', match: 'Match center', team: 'Team page', league: 'Competition page', article: 'Story', player: 'Player page' },
  ar: { noResults: 'لا توجد نتائج مطابقة حالياً.', match: 'مركز المباراة', team: 'صفحة الفريق', league: 'صفحة المسابقة', article: 'مقال', player: 'صفحة اللاعب' },
  fr: { noResults: 'Aucun résultat correspondant pour le moment.', match: 'Centre du match', team: 'Page de l’équipe', league: 'Page de la compétition', article: 'Article', player: 'Page du joueur' },
  es: { noResults: 'Todavía no hay resultados coincidentes.', match: 'Centro del partido', team: 'Página del equipo', league: 'Página de la competición', article: 'Artículo', player: 'Página del jugador' },
}[LANG];
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const slug = value => String(value ?? '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const localName = (item, key) => AR ? item[`${key}Ar`] || item[key] : item[key];
const queryParam = new URLSearchParams(window.location.search).get('q') || '';

async function getJson(path) {
  const response = await fetch(path, { cache: 'no-store' });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

function resultCard(item, type, href, title, excerpt) {
  return `<a class="discovery-card" href="${href}"><div class="news-meta"><span class="news-tag">${esc(copy[type])}</span><span>GlobalScore</span></div><h3>${esc(title)}</h3><p>${esc(excerpt || '')}</p><span class="news-arrow">→</span></a>`;
}

function render(data, query) {
  const target = document.getElementById('globalSearchResults');
  const heading = document.getElementById('searchHeading');
  if (!target || !heading) return;
  heading.textContent = query ? `${document.documentElement.lang === 'ar' ? 'نتائج البحث عن' : 'Results for'} “${query}”` : (document.documentElement.lang === 'ar' ? 'ابدأ بالبحث' : 'Start searching');
  const normalized = query.trim().toLowerCase();
  const results = [];
  const matches = data.live?.matches || data.content?.fixtures || [];
  matches.forEach(match => {
    const fields = [match.home, match.away, match.homeAr, match.awayAr, match.league, match.leagueAr].filter(Boolean).join(' ').toLowerCase();
    if (!normalized || fields.includes(normalized)) results.push(resultCard(match, 'match', `../matches/${encodeURIComponent(match.id)}.html`, `${localName(match, 'home')} – ${localName(match, 'away')}`, `${localName(match, 'league')} · ${match.date || ''} · ${match.time || ''}`));
  });
  const teams = new Map();
  matches.flatMap(match => [match.home, match.away]).filter(Boolean).forEach(team => teams.set(team, team));
  teams.forEach(team => { if (!normalized || team.toLowerCase().includes(normalized)) results.push(resultCard({ }, 'team', `../teams/${slug(team)}.html`, team, AR ? 'المواعيد والنتائج والمقالات المرتبطة بالفريق' : 'Fixtures, results and related stories')); });
  const leagues = new Map();
  matches.forEach(match => { const league = match.league || match.leagueAr; if (league) leagues.set(league, match.leagueEn || league); });
  leagues.forEach((english, label) => { if (!normalized || `${label} ${english}`.toLowerCase().includes(normalized)) results.push(resultCard({}, 'league', `../leagues/${slug(english)}.html`, AR ? label : english, AR ? 'المباريات والترتيب والتغطية المرتبطة' : 'Fixtures, standings and related coverage')); });
  (data.content?.articles || []).forEach(article => {
    const title = localName(article, 'title') || article.title;
    const excerpt = localName(article, 'excerpt') || article.excerpt;
    const fields = `${title} ${excerpt} ${article.category || ''} ${article.categoryAr || ''}`.toLowerCase();
    if (!normalized || fields.includes(normalized)) {
      const href = article.external ? article.href : `../articles/${article.slug}.html`;
      results.push(resultCard(article, 'article', href, title, excerpt));
    }
  });
  const players = Array.isArray(data.players) && data.players.length ? data.players : [
    { name: 'Martin Ødegaard', slug: 'martin-odegaard' },
    { name: 'Bruno Fernandes', slug: 'bruno-fernandes' },
    { name: 'Declan Rice', slug: 'declan-rice' },
    { name: 'Bukayo Saka', slug: 'bukayo-saka' },
    { name: 'Erling Haaland', slug: 'erling-haaland' },
  ];
  players.forEach(({ name, slug: playerSlug }) => {
    if (!normalized || name.toLowerCase().includes(normalized)) results.push(resultCard({}, 'player', `../players/${playerSlug}.html`, name, AR ? 'تحليل اللاعب وبيانات الأداء الموثقة من ESPN عند توفرها' : 'Verified ESPN performance indicators and player profile'));
  });
  target.innerHTML = results.length ? results.slice(0, 60).join('') : `<div class="permanent-empty">${esc(copy.noResults)}</div>`;
}

async function init() {
  const form = document.getElementById('globalSearchForm');
  const input = document.getElementById('globalSearchInput');
  try {
    const [live, content, registry] = await Promise.all([getJson('../../assets/data/live.json?v=4'), getJson('../../assets/data/content.json?v=4'), getJson('../../assets/data/player-registry.json?v=1').catch(() => ({ players: [] }))]);
    const data = { live, content, players: registry.players };
    if (input) input.value = queryParam;
    render(data, queryParam);
    form?.addEventListener('submit', event => {
      event.preventDefault();
      const value = input?.value.trim() || '';
      const url = new URL(window.location.href);
      if (value) url.searchParams.set('q', value); else url.searchParams.delete('q');
      window.history.replaceState({}, '', url);
      render(data, value);
    });
  } catch (error) {
    console.warn('Search index unavailable:', error);
    const target = document.getElementById('globalSearchResults');
    if (target) target.innerHTML = `<div class="permanent-empty">${esc(copy.noResults)}</div>`;
  }
}

init();
