const LANG = window.GLOBAL_LANG || 'en';
const copy = {
  en: { loading: 'Loading verified player data…', ready: 'Verified data loaded', unavailable: 'Player statistics are not available right now.', season: 'Season', starts: 'Starts + sub apps', goals: 'Goals', assists: 'Assists', shots: 'Shots', source: 'Source: ESPN public athlete profile. Values are displayed as reported; GlobalScore does not calculate a player rating.', sourceLink: 'Open ESPN profile', relative: 'Relative scale' },
  ar: { loading: 'جارٍ تحميل بيانات اللاعب الموثقة…', ready: 'تم تحميل البيانات الموثقة', unavailable: 'إحصائيات اللاعب غير متاحة حالياً.', season: 'الموسم', starts: 'بدايات + مشاركات كبديل', goals: 'الأهداف', assists: 'التمريرات الحاسمة', shots: 'التسديدات', source: 'المصدر: ملف اللاعب العام في ESPN. تُعرض القيم كما وردت، ولا يحسب GlobalScore تقييماً للاعب.', sourceLink: 'فتح ملف ESPN', relative: 'مقياس نسبي' },
  fr: { loading: 'Chargement des données vérifiées…', ready: 'Données vérifiées chargées', unavailable: 'Les statistiques du joueur ne sont pas disponibles actuellement.', season: 'Saison', starts: 'Titularisations + entrées', goals: 'Buts', assists: 'Passes décisives', shots: 'Tirs', source: 'Source : profil public du joueur sur ESPN. Les valeurs sont affichées telles que rapportées ; GlobalScore ne calcule pas de note.', sourceLink: 'Ouvrir le profil ESPN', relative: 'Échelle relative' },
  es: { loading: 'Cargando datos verificados…', ready: 'Datos verificados cargados', unavailable: 'Las estadísticas del jugador no están disponibles ahora.', season: 'Temporada', starts: 'Titularidades + entradas', goals: 'Goles', assists: 'Asistencias', shots: 'Tiros', source: 'Fuente: perfil público del jugador en ESPN. Los valores se muestran tal como se reportan; GlobalScore no calcula una valoración.', sourceLink: 'Abrir perfil de ESPN', relative: 'Escala relativa' },
}[LANG];
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const number = value => Number.parseFloat(String(value ?? '').replace(/[^0-9.]/g, '')) || 0;
const percent = value => Math.max(8, Math.min(100, Math.round(value)));

function metricDefinitions() {
  return [
    { key: 'starts-subIns', label: copy.starts },
    { key: 'totalGoals', label: copy.goals },
    { key: 'goalAssists', label: copy.assists },
    { key: 'totalShots', label: copy.shots },
  ];
}

function renderKpis(stats) {
  const target = document.getElementById('playerPerformanceKpis');
  if (!target) return;
  target.innerHTML = metricDefinitions().map(definition => {
    const stat = stats.find(item => item.name === definition.key) || {};
    return `<div class="performance-kpi"><span>${esc(definition.label)}</span><strong>${esc(stat.displayValue || '—')}</strong></div>`;
  }).join('');
}

function renderBars(stats) {
  const target = document.getElementById('playerPerformanceBars');
  if (!target) return;
  const definitions = metricDefinitions();
  const values = definitions.map(definition => number((stats.find(item => item.name === definition.key) || {}).value));
  const maximum = Math.max(...values, 1);
  target.innerHTML = definitions.map((definition, index) => {
    const stat = stats.find(item => item.name === definition.key) || {};
    const value = values[index];
    return `<div class="performance-bar-row" title="${esc(stat.description || definition.label)}"><div class="performance-bar-label"><span>${esc(definition.label)}</span><strong>${esc(stat.displayValue || '—')}</strong></div><div class="performance-bar-track"><span style="width:${percent((value / maximum) * 100)}%"></span></div></div>`;
  }).join('');
}

function renderRadar(stats) {
  const target = document.getElementById('playerPerformanceRadar');
  if (!target) return;
  const definitions = metricDefinitions();
  const values = definitions.map(definition => number((stats.find(item => item.name === definition.key) || {}).value));
  const maximum = Math.max(...values, 1);
  const center = 120;
  const radius = 78;
  const points = values.map((value, index) => {
    const angle = -Math.PI / 2 + index * Math.PI / 2;
    const ratio = Math.max(.08, value / maximum);
    return `${center + Math.cos(angle) * radius * ratio},${center + Math.sin(angle) * radius * ratio}`;
  }).join(' ');
  const outer = [0, 1, 2, 3].map(index => {
    const angle = -Math.PI / 2 + index * Math.PI / 2;
    return `${center + Math.cos(angle) * radius},${center + Math.sin(angle) * radius}`;
  }).join(' ');
  const labels = definitions.map((definition, index) => {
    const angle = -Math.PI / 2 + index * Math.PI / 2;
    const x = center + Math.cos(angle) * 104;
    const y = center + Math.sin(angle) * 104;
    return `<text x="${x}" y="${y}" text-anchor="middle" class="performance-radar-label">${esc(definition.label)}</text>`;
  }).join('');
  target.innerHTML = `<svg viewBox="0 0 240 240" role="img" aria-label="${esc(copy.relative)}"><polygon points="${outer}" class="performance-radar-grid"></polygon><polygon points="${points}" class="performance-radar-shape"></polygon>${labels}</svg><small>${esc(copy.relative)}</small>`;
}

async function init() {
  const panel = document.getElementById('playerPerformance');
  if (!panel) return;
  const status = document.getElementById('playerPerformanceStatus');
  const playerId = panel.dataset.playerId;
  const leagueCode = panel.dataset.leagueCode || 'eng.1';
  const source = document.getElementById('playerPerformanceSource');
  const endpoint = `https://site.web.api.espn.com/apis/common/v3/sports/soccer/${encodeURIComponent(leagueCode)}/athletes/${encodeURIComponent(playerId)}`;
  try {
    const response = await fetch(endpoint, { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    const athlete = payload.athlete || {};
    const stats = athlete.statsSummary?.statistics || [];
    if (!stats.length) throw new Error('No statistics');
    renderKpis(stats);
    renderBars(stats);
    renderRadar(stats);
    if (status) status.textContent = `${copy.ready} · ${copy.season}: ${esc(payload.season?.displayName || athlete.statsSummary?.displayName || '—')}`;
    if (source) source.innerHTML = `${esc(copy.source)} <a href="https://www.espn.com/soccer/player/stats/_/id/${encodeURIComponent(playerId)}" target="_blank" rel="noopener noreferrer">${esc(copy.sourceLink)}</a>`;
  } catch (error) {
    console.warn('Player performance unavailable:', error);
    if (status) status.textContent = copy.unavailable;
    if (source) source.textContent = copy.source;
  }
}

init();
