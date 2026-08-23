const LANG = window.GLOBAL_LANG || 'en';

const COPY = {
  en: { loading: 'Loading both player profiles…', ready: 'Verified comparison loaded', unavailable: 'One or both player profiles are unavailable right now.', season: 'Season', starts: 'Starts + sub apps', goals: 'Goals', assists: 'Assists', shots: 'Shots', playerOne: 'Player one', playerTwo: 'Player two', compare: 'Compare now', source: 'Source: ESPN public athlete profiles. Values are displayed as reported; GlobalScore does not calculate a player rating.', open: 'Open ESPN profile', relative: 'Relative scale', sameSeason: 'Same season summary' },
  ar: { loading: 'جارٍ تحميل ملفي اللاعبين…', ready: 'تم تحميل المقارنة الموثقة', unavailable: 'ملف أحد اللاعبين أو كلاهما غير متاح حالياً.', season: 'الموسم', starts: 'بدايات + مشاركات كبديل', goals: 'الأهداف', assists: 'التمريرات الحاسمة', shots: 'التسديدات', playerOne: 'اللاعب الأول', playerTwo: 'اللاعب الثاني', compare: 'بدء المقارنة', source: 'المصدر: ملفات اللاعبين العامة في ESPN. تُعرض القيم كما وردت، ولا يحسب GlobalScore تقييماً للاعب.', open: 'فتح ملف ESPN', relative: 'مقياس نسبي', sameSeason: 'الملخص الموسمي نفسه' },
  fr: { loading: 'Chargement des deux profils…', ready: 'Comparaison vérifiée chargée', unavailable: 'Un ou deux profils ne sont pas disponibles actuellement.', season: 'Saison', starts: 'Titularisations + entrées', goals: 'Buts', assists: 'Passes décisives', shots: 'Tirs', playerOne: 'Joueur 1', playerTwo: 'Joueur 2', compare: 'Comparer', source: 'Source : profils publics des joueurs sur ESPN. Les valeurs sont affichées telles que rapportées ; GlobalScore ne calcule pas de note.', open: 'Ouvrir le profil ESPN', relative: 'Échelle relative', sameSeason: 'Même résumé de saison' },
  es: { loading: 'Cargando ambos perfiles…', ready: 'Comparación verificada cargada', unavailable: 'Uno o ambos perfiles no están disponibles ahora.', season: 'Temporada', starts: 'Titularidades + entradas', goals: 'Goles', assists: 'Asistencias', shots: 'Tiros', playerOne: 'Jugador uno', playerTwo: 'Jugador dos', compare: 'Comparar ahora', source: 'Fuente: perfiles públicos de jugadores en ESPN. Los valores se muestran tal como se reportan; GlobalScore no calcula una valoración.', open: 'Abrir perfil de ESPN', relative: 'Escala relativa', sameSeason: 'Mismo resumen de temporada' },
}[LANG] || {};

const PLAYERS = [
  { id: '203669', name: 'Martin Ødegaard', team: 'Arsenal', slug: 'martin-odegaard' },
  { id: '124091', name: 'Bruno Fernandes', team: 'Manchester United', slug: 'bruno-fernandes' },
  { id: '238262', name: 'Declan Rice', team: 'Arsenal', slug: 'declan-rice' },
];

const METRICS = [
  { key: 'starts-subIns', label: COPY.starts },
  { key: 'totalGoals', label: COPY.goals },
  { key: 'goalAssists', label: COPY.assists },
  { key: 'totalShots', label: COPY.shots },
];

const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
const numericValue = value => Number.parseFloat(String(value ?? '').replace(/[^0-9.]/g, '')) || 0;
const metricNumber = stat => { const raw = stat?.value ?? stat?.displayValue; return raw === undefined || raw === null || raw === '' ? null : numericValue(raw); };
const playerById = id => PLAYERS.find(player => player.id === String(id)) || PLAYERS[0];

function statsFor(payload) {
  return payload?.athlete?.statsSummary?.statistics || [];
}

function metricValue(stats, key) {
  return stats.find(stat => stat.name === key) || {};
}

function populateSelect(select, selectedId) {
  if (!select) return;
  select.innerHTML = PLAYERS.map(player => `<option value="${player.id}"${player.id === selectedId ? ' selected' : ''}>${escapeHtml(player.name)} · ${escapeHtml(player.team)}</option>`).join('');
}

function renderIdentity(target, player, stats) {
  if (!target) return;
  target.innerHTML = `<div class="compare-player-name">${escapeHtml(player.name)}</div><div class="compare-player-team">${escapeHtml(player.team)}</div><div class="compare-player-kpis">${METRICS.map(metric => `<div><span>${escapeHtml(metric.label)}</span><strong>${escapeHtml(metricValue(stats, metric.key).displayValue || '—')}</strong></div>`).join('')}</div>`;
}

function renderBars(target, left, right) {
  if (!target) return;
  target.innerHTML = METRICS.map(metric => {
    const leftStat = metricValue(left.stats, metric.key);
    const rightStat = metricValue(right.stats, metric.key);
    const leftValue = metricNumber(leftStat);
    const rightValue = metricNumber(rightStat);
    const maximum = Math.max(leftValue ?? 0, rightValue ?? 0, 1);
    const leftWidth = leftValue === null ? 0 : Math.round(leftValue / maximum * 100);
    const rightWidth = rightValue === null ? 0 : Math.round(rightValue / maximum * 100);
    return `<div class="compare-bar-row"><div class="compare-bar-label"><span>${escapeHtml(metric.label)}</span><strong>${escapeHtml(leftStat.displayValue || '—')} <em>·</em> ${escapeHtml(rightStat.displayValue || '—')}</strong></div><div class="compare-bar-track"><span class="compare-bar-left" style="width:${leftWidth}%"></span><span class="compare-bar-right" style="width:${rightWidth}%"></span></div></div>`;
  }).join('');
}

function radarPoints(values, radius = 78) {
  const center = 120;
  return values.map((value, index) => {
    const angle = -Math.PI / 2 + index * Math.PI / 2;
    const ratio = Math.max(0, value / Math.max(...values, 1));
    return `${center + Math.cos(angle) * radius * ratio},${center + Math.sin(angle) * radius * ratio}`;
  }).join(' ');
}

function renderRadar(target, left, right) {
  if (!target) return;
  const leftValues = METRICS.map(metric => metricNumber(metricValue(left.stats, metric.key)));
  const rightValues = METRICS.map(metric => metricNumber(metricValue(right.stats, metric.key)));
  const maximum = Math.max(...leftValues.map(value => value ?? 0), ...rightValues.map(value => value ?? 0), 1);
  const outer = [0, 1, 2, 3].map(index => {
    const angle = -Math.PI / 2 + index * Math.PI / 2;
    return `${120 + Math.cos(angle) * 78},${120 + Math.sin(angle) * 78}`;
  }).join(' ');
  const labels = METRICS.map((metric, index) => {
    const angle = -Math.PI / 2 + index * Math.PI / 2;
    return `<text x="${120 + Math.cos(angle) * 104}" y="${120 + Math.sin(angle) * 104}" text-anchor="middle" class="performance-radar-label">${escapeHtml(metric.label)}</text>`;
  }).join('');
  const leftNormalized = leftValues.map(value => (value ?? 0) / maximum);
  const rightNormalized = rightValues.map(value => (value ?? 0) / maximum);
  target.innerHTML = `<svg viewBox="0 0 240 240" role="img" aria-label="${escapeHtml(COPY.relative)}"><polygon points="${outer}" class="performance-radar-grid"></polygon><polygon points="${radarPoints(leftNormalized)}" class="compare-radar-left"></polygon><polygon points="${radarPoints(rightNormalized)}" class="compare-radar-right"></polygon>${labels}</svg><div class="compare-legend"><span><i class="compare-dot compare-dot-left"></i>${escapeHtml(left.player.name)}</span><span><i class="compare-dot compare-dot-right"></i>${escapeHtml(right.player.name)}</span></div><small>${escapeHtml(COPY.relative)}</small>`;
}

async function loadPlayer(player) {
  const endpoint = `https://site.web.api.espn.com/apis/common/v3/sports/soccer/eng.1/athletes/${encodeURIComponent(player.id)}`;
  const response = await fetch(endpoint, { cache: 'no-store' });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const payload = await response.json();
  const stats = statsFor(payload);
  if (!stats.length) throw new Error('No statistics');
  return { player, payload, stats, season: payload.season?.displayName || payload.athlete?.statsSummary?.displayName || '—' };
}

async function compare() {
  const panel = document.getElementById('playerCompare');
  if (!panel) return;
  const status = document.getElementById('playerCompareStatus');
  const source = document.getElementById('playerCompareSource');
  const selectOne = document.getElementById('comparePlayerOne');
  const selectTwo = document.getElementById('comparePlayerTwo');
  const leftPlayer = playerById(selectOne?.value || new URLSearchParams(location.search).get('p1') || '203669');
  const rightPlayer = playerById(selectTwo?.value || new URLSearchParams(location.search).get('p2') || '124091');
  if (leftPlayer.id === rightPlayer.id) {
    if (status) status.textContent = COPY.unavailable;
    return;
  }
  if (status) status.textContent = COPY.loading;
  try {
    const [left, right] = await Promise.all([loadPlayer(leftPlayer), loadPlayer(rightPlayer)]);
    renderIdentity(document.getElementById('comparePlayerCardOne'), left.player, left.stats);
    renderIdentity(document.getElementById('comparePlayerCardTwo'), right.player, right.stats);
    renderBars(document.getElementById('playerCompareBars'), left, right);
    renderRadar(document.getElementById('playerCompareRadar'), left, right);
    const seasonsMatch = left.season === right.season;
    if (status) status.textContent = `${COPY.ready} · ${COPY.season}: ${escapeHtml(left.season)}${seasonsMatch ? '' : ` · ${COPY.sameSeason}: —`}`;
    if (source) source.innerHTML = `${escapeHtml(COPY.source)} <a href="https://www.espn.com/soccer/player/stats/_/id/${encodeURIComponent(left.player.id)}" target="_blank" rel="noopener noreferrer">${escapeHtml(left.player.name)}</a> · <a href="https://www.espn.com/soccer/player/stats/_/id/${encodeURIComponent(right.player.id)}" target="_blank" rel="noopener noreferrer">${escapeHtml(right.player.name)}</a>`;
    const query = new URLSearchParams({ p1: left.player.id, p2: right.player.id });
    history.replaceState({}, '', `${location.pathname}?${query}`);
  } catch (error) {
    console.warn('Player comparison unavailable:', error);
    if (status) status.textContent = COPY.unavailable;
    if (source) source.textContent = COPY.source;
  }
}

function init() {
  const selectOne = document.getElementById('comparePlayerOne');
  const selectTwo = document.getElementById('comparePlayerTwo');
  const params = new URLSearchParams(location.search);
  populateSelect(selectOne, playerById(params.get('p1') || '203669').id);
  populateSelect(selectTwo, playerById(params.get('p2') || '124091').id);
  document.getElementById('playerCompareForm')?.addEventListener('submit', event => { event.preventDefault(); compare(); });
  compare();
}

init();
