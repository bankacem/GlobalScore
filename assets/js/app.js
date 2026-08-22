import { DataSource } from './data-source.js';
import { MatchComponent, LeagueTableComponent, MatchDetailModalComponent } from './components.js';
import { setupTheme, getFavorites } from './utils.js';

const dataSource = new DataSource();
let allMatches = [];
let allTables = {};
let content = { fixtures: [], articles: [] };
let currentView = '#today';
let activeSearchQuery = '';

const isArabic = () => document.documentElement.lang === 'ar';
const text = (item, key) => isArabic() ? item[`${key}Ar`] : item[key];

function safeLink(article) {
  return article.href || `articles/${article.slug}.html`;
}

function renderCurrentState() {
  const container = document.getElementById('liveMatches');
  if (!container) return;
  const ar = isArabic();
  let displayed = [...allMatches];
  if (currentView === '#live') displayed = displayed.filter(match => match.status === 'Live');
  if (currentView === '#yesterday') displayed = displayed.filter(match => match.status === 'FT');
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
  container.innerHTML = content.fixtures.map(fixture => `<article class="fixture-card"><div class="fixture-date"><strong>${text(fixture, 'day')}</strong>${text(fixture, 'month')}</div><div class="fixture-body"><div class="fixture-league">${text(fixture, 'league')}</div><div class="fixture-teams"><span>${text(fixture, 'home')}</span><span>${fixture.time}</span><span>${text(fixture, 'away')}</span></div></div></article>`).join('');
}

function renderNews() {
  const container = document.getElementById('newsList');
  if (!container) return;
  container.innerHTML = content.articles.map(article => `<a class="news-card" href="${safeLink(article)}"><div class="news-meta"><span class="news-tag">${text(article, 'category')}</span><span>${text(article, 'readTime')}</span></div><h3>${text(article, 'title')}</h3><p>${text(article, 'excerpt')}</p><span class="news-arrow">${isArabic() ? '←' : '→'}</span></a>`).join('');
}

function renderLeagueSummary() {
  const container = document.getElementById('leagueSummary');
  if (!container) return;
  const arabicLeagues = {'Premier League':'الدوري الإنجليزي الممتاز','La Liga':'الدوري الإسباني','Egyptian Premier League':'الدوري المصري الممتاز','Champions League':'دوري أبطال أوروبا'};
  container.innerHTML = Object.entries(allTables).slice(0, 4).map(([league, rows]) => `<a href="#leagues"><span>${isArabic() ? (arabicLeagues[league] || league) : league}</span><span>${rows.length} ${isArabic() ? 'فرق' : 'teams'}</span></a>`).join('');
}

function showMatchDetails(id) {
  const match = allMatches.find(item => Number(item.id) === Number(id));
  if (!match) return;
  document.getElementById('matchDetailsModal')?.remove();
  document.body.appendChild(MatchDetailModalComponent(match, renderCurrentState));
}

function setupNavigation() {
  document.querySelectorAll('.nav-link').forEach(link => link.addEventListener('click', () => {
    document.querySelectorAll('.nav-link').forEach(item => item.classList.remove('active'));
    link.classList.add('active');
    currentView = link.getAttribute('href');
    if (currentView === '#leagues') {
      const target = document.getElementById('liveMatches');
      if (target) {
        target.innerHTML = '';
        Object.entries(allTables).forEach(([league, rows]) => { const title = document.createElement('h3'); title.className = 'table-league-title'; title.textContent = `🏆 ${league}`; target.appendChild(title); target.appendChild(LeagueTableComponent(rows)); });
      }
    } else renderCurrentState();
  }));
}

async function initApp() {
  setupTheme();
  const data = await dataSource.getLiveMatches();
  allMatches = data.matches || [];
  allTables = data.tables || {};
  content = await dataSource.getContent();
  document.getElementById('searchBar')?.addEventListener('input', event => { activeSearchQuery = event.target.value; renderCurrentState(); });
  setupNavigation();
  renderCurrentState();
  renderFixtures();
  renderNews();
  renderLeagueSummary();
}

document.addEventListener('DOMContentLoaded', initApp);
if ('serviceWorker' in navigator) window.addEventListener('load', () => navigator.serviceWorker.register('../sw.js').catch(() => {}));
