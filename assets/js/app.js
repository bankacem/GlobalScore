import { DataSource } from './data-source.js?v=8';
import { MatchComponent, LeagueTableComponent, MatchDetailModalComponent } from './components.js?v=10';
import { setupTheme, getFavorites, requestNotifications } from './utils.js?v=5';

const dataSource = new DataSource();
let allMatches = [];
let allTables = {};
let liveStandings = [];
let content = { fixtures: [], articles: [] };
let currentView = '#today';
let activeSearchQuery = '';

const isArabic = () => document.documentElement.lang === 'ar';
const isoDate = (offset = 0) => { const date = new Date(); date.setDate(date.getDate() + offset); return date.toISOString().slice(0, 10); };
let selectedDate = new URLSearchParams(window.location.search).get('date') || isoDate();
const text = (item, key) => isArabic() ? item[`${key}Ar`] : item[key];
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const teamSlug = value => String(value ?? '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

function safeLink(article) {
  return article.href || `articles/${article.slug}.html`;
}

function renderCurrentState() {
  const container = document.getElementById('liveMatches');
  if (!container) return;
  const ar = isArabic();
  let displayed = [...allMatches];
  if (currentView === '#today') displayed = displayed.filter(match => !match.date || match.date === selectedDate);
  if (currentView === '#live') displayed = displayed.filter(match => match.status === 'Live');
  if (currentView === '#yesterday') displayed = displayed.filter(match => match.date === selectedDate && match.status === 'FT');
  if (currentView === '#favorites') displayed = displayed.filter(match => getFavorites().includes(Number(match.id)));
  if (activeSearchQuery) {
    const query = activeSearchQuery.toLowerCase();
    displayed = displayed.filter(match => [match.home, match.away, match.homeAr, match.awayAr, match.league, match.leagueAr].some(value => value.toLowerCase().includes(query)));
  }
  container.innerHTML = '';
  if (!displayed.length) {
    container.innerHTML = `<div class="empty-state">${ar ? 'لا توجد مباريات مطابقة حالياً.' : 'No matches match your search.'}</div>`;
    return;
  }
  const groups = {};
  displayed.forEach(match => {
    const league = ar ? match.leagueAr : match.league;
    (groups[league] ||= []).push(match);
  });
  Object.entries(groups).forEach(([league, matches]) => {
    const header = document.createElement('div');
    header.className = 'league-header';
    header.innerHTML = `<h3>${league}</h3>`;
    container.appendChild(header);
    matches.forEach(match => container.appendChild(MatchComponent(match, () => showMatchDetails(match.id))));
  });
}

function renderFixtures() {
  const container = document.getElementById('fixtureList');
  if (!container) return;
  container.innerHTML = content.fixtures.map(fixture => {
    const home = text(fixture, 'home');
    const away = text(fixture, 'away');
    const league = text(fixture, 'league');
    const matchUrl = fixture.id ? `matches/${encodeURIComponent(fixture.id)}.html` : '#today';
    const leagueUrl = `leagues/${teamSlug(fixture.league || league)}.html`;
    return `<article class="fixture-card"><div class="fixture-date"><strong>${escapeHtml(text(fixture, 'day'))}</strong>${escapeHtml(text(fixture, 'month'))}</div><div class="fixture-body"><a class="fixture-league" href="${leagueUrl}">${escapeHtml(league)}</a><div class="fixture-teams"><a class="fixture-team fixture-home" href="teams/${teamSlug(fixture.home || home)}.html" title="${escapeHtml(home)}">${escapeHtml(home)}</a><a class="fixture-time" href="${matchUrl}" title="${isArabic() ? 'فتح صفحة المباراة' : 'Open match center'}">${escapeHtml(fixture.time)}<small>${isArabic() ? 'مركز المباراة' : 'Match center'}</small></a><a class="fixture-team fixture-away" href="teams/${teamSlug(fixture.away || away)}.html" title="${escapeHtml(away)}">${escapeHtml(away)}</a></div></div></article>`;
  }).join('');
}

function renderNews() {
  const container = document.getElementById('newsList');
  if (!container) return;
  container.innerHTML = content.articles.map(article => {
    const external = article.external ? ' target="_blank" rel="noopener noreferrer"' : '';
    const source = article.source ? ` · ${article.source}` : '';
    return `<a class="news-card" href="${safeLink(article)}"${external}><div class="news-meta"><span class="news-tag">${text(article, 'category')}</span><span>${text(article, 'readTime')}${source}</span></div><h3>${text(article, 'title')}</h3><p>${text(article, 'excerpt')}</p><span class="news-arrow">${isArabic() ? '←' : '→'}</span></a>`;
  }).join('');
}

function renderLeagueSummary() {
  const container = document.getElementById('leagueSummary');
  if (!container) return;
  const arabicLeagues = {'Premier League':'الدوري الإنجليزي الممتاز','La Liga':'الدوري الإسباني','Egyptian Premier League':'الدوري المصري الممتاز','Champions League':'دوري أبطال أوروبا'};
  const summary = liveStandings.length ? liveStandings.map(item => [isArabic() ? item.leagueAr : item.league, item.groups.reduce((total, group) => total + group.rows.length, 0)]) : Object.entries(allTables);
  container.innerHTML = summary.slice(0, 4).map(([league, count]) => `<a href="#leagues"><span>${isArabic() ? (arabicLeagues[league] || league) : league}</span><span>${count} ${isArabic() ? 'فرق' : 'teams'}</span></a>`).join('');
}

function renderStandings() {
  const target = document.getElementById('liveMatches');
  if (!target) return;
  target.innerHTML = '';
  if (liveStandings.length) {
    liveStandings.forEach(league => league.groups.forEach(group => {
      const title = document.createElement('h3');
      title.className = 'table-league-title';
      title.textContent = `🏆 ${isArabic() ? league.leagueAr : league.league}${league.groups.length > 1 ? ` · ${group.name}` : ''}`;
      target.appendChild(title);
      target.appendChild(LeagueTableComponent(group.rows, { live: true }));
    }));
  } else {
    Object.entries(allTables).forEach(([league, rows]) => { const title = document.createElement('h3'); title.className = 'table-league-title'; title.textContent = `🏆 ${isArabic() ? league : league}`; target.appendChild(title); target.appendChild(LeagueTableComponent(rows)); });
  }
}

async function showMatchDetails(id) {
  const match = allMatches.find(item => Number(item.id) === Number(id));
  if (!match) return;
  document.getElementById('matchDetailsModal')?.remove();
  const initialModal = MatchDetailModalComponent(match, renderCurrentState);
  document.body.appendChild(initialModal);
  const details = await dataSource.getMatchDetails(match);
  if (!document.body.contains(initialModal)) return;
  match.details = details || {};
  initialModal.replaceWith(MatchDetailModalComponent(match, renderCurrentState));
}

function setupNavigation() {
  document.querySelectorAll('.nav-link').forEach(link => link.addEventListener('click', () => {
    document.querySelectorAll('.nav-link').forEach(item => item.classList.remove('active'));
    link.classList.add('active');
    currentView = link.getAttribute('href');
    if (currentView === '#yesterday') selectedDate = isoDate(-1);
    if (currentView === '#today') selectedDate = isoDate();
    if (currentView === '#leagues') {
      const target = document.getElementById('liveMatches');
      if (target) {
        target.innerHTML = '';
        renderStandings();
      }
    } else renderCurrentState();
  }));
}

function setupDateControls() {
  const picker = document.getElementById('datePicker');
  const label = document.getElementById('dateToday');
  if (!picker || !label) return;
  picker.value = selectedDate;
  const apply = date => { if (!date) return; selectedDate = date; picker.value = date; currentView = '#today'; renderCurrentState(); label.textContent = date === isoDate() ? (isArabic() ? 'اليوم' : 'Today') : date; };
  document.getElementById('datePrev')?.addEventListener('click', () => { const d = new Date(`${selectedDate}T12:00:00`); d.setDate(d.getDate() - 1); apply(d.toISOString().slice(0, 10)); });
  document.getElementById('dateNext')?.addEventListener('click', () => { const d = new Date(`${selectedDate}T12:00:00`); d.setDate(d.getDate() + 1); apply(d.toISOString().slice(0, 10)); });
  label.addEventListener('click', () => apply(isoDate()));
  picker.addEventListener('change', event => apply(event.target.value));
}

function setupNotificationControl() {
  const button = document.getElementById('notifyToggle');
  if (!button) return;
  button.addEventListener('click', async () => { const result = await requestNotifications(); button.textContent = result === 'granted' ? (isArabic() ? 'التنبيهات مفعلة' : 'Alerts enabled') : (isArabic() ? 'لم يتم التفعيل' : 'Alerts unavailable'); });
}

async function refreshEspnMatches() {
  const liveMatches = await dataSource.getEspnMatches();
  if (!liveMatches.length) return false;
  const previous = new Map(allMatches.map(match => [String(match.id), match.score]));
  const snapshot = allMatches.filter(match => match.date !== isoDate());
  const byId = new Map([...snapshot, ...liveMatches].map(match => [String(match.id), match]));
  allMatches = [...byId.values()];
  if ('Notification' in window && Notification.permission === 'granted') liveMatches.forEach(match => {
    if (getFavorites().includes(Number(match.id)) && previous.has(String(match.id)) && previous.get(String(match.id)) !== match.score) new Notification(`${match.home} ${match.score} ${match.away}`, { body: match.status === 'FT' ? (isArabic() ? 'انتهت المباراة' : 'Full time') : (isArabic() ? 'تغيرت النتيجة' : 'Score update') });
  });
  renderCurrentState();
  return true;
}

function setLiveStatus() {
  const status = document.getElementById('dataStatus');
  const description = document.getElementById('dataDescription');
  if (status) status.textContent = isArabic() ? 'بث ESPN مباشر' : 'ESPN live feed';
  if (description) description.textContent = isArabic() ? 'تحديث تلقائي كل 15 ثانية' : 'Auto-refresh every 15 seconds';
}

async function initApp() {
  setupTheme();
  setupDateControls();
  setupNotificationControl();
  const data = await dataSource.getLiveMatches();
  allTables = data.tables || {};
  const [contentData, standingsData] = await Promise.all([dataSource.getContent(), dataSource.getAllStandings()]);
  content = contentData;
  liveStandings = standingsData;
  allMatches = data.matches || [];
  const espnAvailable = await refreshEspnMatches();
  const searchBar = document.getElementById('searchBar');
  searchBar?.addEventListener('input', event => { activeSearchQuery = event.target.value; renderCurrentState(); });
  searchBar?.addEventListener('keydown', event => {
    if (event.key === 'Enter' && searchBar.value.trim()) {
      window.location.href = `search/?q=${encodeURIComponent(searchBar.value.trim())}`;
    }
  });
  setupNavigation();
  if (espnAvailable) setLiveStatus();
  else renderCurrentState();
  renderFixtures();
  renderNews();
  renderLeagueSummary();
  const status = document.getElementById('dataStatus');
  const description = document.getElementById('dataDescription');
  if (!espnAvailable && status && content.lastUpdated) {
    const updated = new Date(content.lastUpdated);
    const stamp = Number.isNaN(updated.getTime()) ? content.lastUpdated : updated.toLocaleString(isArabic() ? 'ar' : 'en', {dateStyle: 'medium', timeStyle: 'short'});
    status.textContent = isArabic() ? 'بيانات محدثة' : 'Updated snapshot';
    if (description) description.textContent = isArabic() ? `آخر تحديث: ${stamp}` : `Last refresh: ${stamp}`;
  }
  if (espnAvailable) window.setInterval(async () => { if (await refreshEspnMatches()) setLiveStatus(); }, 15000);
  window.setInterval(async () => { const refreshed = await dataSource.getAllStandings(); if (refreshed.length) { liveStandings = refreshed; renderLeagueSummary(); if (currentView === '#leagues') renderStandings(); } }, 600000);
}

document.addEventListener('DOMContentLoaded', initApp);
if ('serviceWorker' in navigator) window.addEventListener('load', () => navigator.serviceWorker.register('../sw.js').catch(() => {}));
