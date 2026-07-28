import { DataSource } from './data-source.js';
import { Router } from './router.js';
import {
  MatchComponent,
  LeagueTableComponent,
  MatchDetailModalComponent,
  ToastNotification
} from './components.js';
import {
  setupTheme,
  setupLanguageToggle,
  getFavorites
} from './utils.js';

const dataSource = new DataSource();
let allMatches = [];
let allTables = {};
let currentView = '#today';
let activeFilterLeague = '';
let activeSearchQuery = '';

// Live Match Simulator config
function startLiveSimulator() {
  setInterval(() => {
    let scoreChanged = false;
    let scorer = '';
    let goalMatch = null;

    allMatches = allMatches.map(match => {
      if (match.status === 'Live') {
        // Increment minute
        const nextMin = match.minute + 1;
        match.minute = nextMin > 90 ? 90 : nextMin;

        // Random chance of goal (1.5%)
        if (Math.random() < 0.015) {
          scoreChanged = true;
          const scores = match.score.split('-').map(s => parseInt(s.trim()));
          const isHomeScoring = Math.random() > 0.5;
          if (isHomeScoring) {
            scores[0]++;
            scorer = document.documentElement.lang === 'ar' ? `${match.homeAr} يسجل!` : `${match.home} Scores!`;
          } else {
            scores[1]++;
            scorer = document.documentElement.lang === 'ar' ? `${match.awayAr} يسجل!` : `${match.away} Scores!`;
          }
          match.score = `${scores[0]} - ${scores[1]}`;
          goalMatch = match;

          // Push event to match timeline
          const eventItem = {
            minute: match.minute,
            player: isHomeScoring ? "Scorer Goal" : "Away Goal",
            playerAr: isHomeScoring ? "مسجل الهدف" : "هدف الضيف",
            type: "Goal",
            typeAr: "هدف",
            score: match.score
          };
          match.events = match.events || [];
          match.events.push(eventItem);
        }
      }
      return match;
    });

    if (scoreChanged && goalMatch) {
      ToastNotification(
        document.documentElement.lang === 'ar' ? `⚽ هدف جديد! ${goalMatch.homeAr} ${goalMatch.score} ${goalMatch.awayAr}` : `⚽ GOAL! ${goalMatch.home} ${goalMatch.score} ${goalMatch.away}`,
        scorer
      );
    }

    // Live update UI elements without hard reloading entire page structure
    renderCurrentState();
  }, 5000); // simulation runs every 5 seconds
}

// Render Engine
function renderCurrentState() {
  const isAr = document.documentElement.lang === 'ar';

  // Highlight active tab
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.remove('active');
    const href = link.getAttribute('href');
    if (href === currentView) {
      link.classList.add('active');
    }
  });

  const matchesContainer = document.getElementById('liveMatches');
  if (!matchesContainer) return;

  // Clear or build skeleton
  matchesContainer.innerHTML = '';

  // Get filtered elements based on current tab state
  let displayed = [...allMatches];

  // 1. Tab View Filter
  if (currentView === '#live') {
    displayed = displayed.filter(m => m.status === 'Live');
  } else if (currentView === '#yesterday') {
    displayed = displayed.filter(m => m.status === 'FT');
  } else if (currentView === '#favorites') {
    const favs = getFavorites();
    displayed = displayed.filter(m => favs.includes(Number(m.id)));
  }

  // 2. League sidebar filter if active
  if (activeFilterLeague) {
    displayed = displayed.filter(m => m.league === activeFilterLeague);
  }

  // 3. Search query filter if active
  if (activeSearchQuery) {
    const q = activeSearchQuery.toLowerCase();
    displayed = displayed.filter(m =>
      m.home.toLowerCase().includes(q) ||
      m.away.toLowerCase().includes(q) ||
      m.homeAr.toLowerCase().includes(q) ||
      m.awayAr.toLowerCase().includes(q) ||
      m.league.toLowerCase().includes(q) ||
      m.leagueAr.toLowerCase().includes(q)
    );
  }

  if (displayed.length === 0) {
    matchesContainer.innerHTML = `<div class="loading">${isAr ? 'لا توجد مباريات مطابقة.' : 'No matches match your criteria.'}</div>`;
    return;
  }

  // Group by league for premium experience
  const groupedByLeague = {};
  displayed.forEach(m => {
    const leagueName = isAr ? m.leagueAr : m.league;
    if (!groupedByLeague[leagueName]) {
      groupedByLeague[leagueName] = [];
    }
    groupedByLeague[leagueName].push(m);
  });

  for (const [leagueName, matchList] of Object.entries(groupedByLeague)) {
    // Create league title segment
    const headerDiv = document.createElement('div');
    headerDiv.className = 'league-header';
    headerDiv.innerHTML = `<h3>🏆 ${leagueName}</h3>`;
    matchesContainer.appendChild(headerDiv);

    matchList.forEach(match => {
      const card = MatchComponent(match, () => {
        // Show match detail modal on click
        showMatchDetails(match.id);
      });
      matchesContainer.appendChild(card);
    });
  }
}

// Match details modal trigger
function showMatchDetails(id) {
  const match = allMatches.find(m => m.id === Number(id));
  if (!match) return;

  // If previous modal exists, remove it
  const oldModal = document.getElementById('matchDetailsModal');
  if (oldModal) oldModal.remove();

  const modal = MatchDetailModalComponent(match, () => {
    // on favorite toggled, re-render main list
    renderCurrentState();
  });
  document.body.appendChild(modal);
}

// Show League tables view
function renderLeaguesView() {
  const container = document.getElementById('liveMatches');
  if (!container) return;
  container.innerHTML = '';

  const isAr = document.documentElement.lang === 'ar';

  if (Object.keys(allTables).length === 0) {
    container.innerHTML = `<div class="loading">${isAr ? 'جاري تحميل جدول الترتيب...' : 'Loading tables...'}</div>`;
    return;
  }

  for (const [leagueName, tableRows] of Object.entries(allTables)) {
    const leagueTitle = document.createElement('h3');
    leagueTitle.className = 'table-league-title';
    leagueTitle.textContent = `🏆 ${leagueName}`;
    container.appendChild(leagueTitle);

    const tableEl = LeagueTableComponent(tableRows);
    container.appendChild(tableEl);
  }
}

// Initialise core modules
async function initApp() {
  setupTheme();
  setupLanguageToggle();

  // Load resources
  const data = await dataSource.getLiveMatches();
  allMatches = data.matches || [];
  allTables = data.tables || {};

  // Setup search dynamic filtering
  const searchBar = document.getElementById('searchBar');
  if (searchBar) {
    searchBar.addEventListener('input', (e) => {
      activeSearchQuery = e.target.value;
      if (currentView !== '#leagues') {
        renderCurrentState();
      }
    });
  }

  // Setup routes mapping
  const routes = {
    '#today': () => {
      currentView = '#today';
      activeFilterLeague = '';
      renderCurrentState();
    },
    '#live': () => {
      currentView = '#live';
      activeFilterLeague = '';
      renderCurrentState();
    },
    '#yesterday': () => {
      currentView = '#yesterday';
      activeFilterLeague = '';
      renderCurrentState();
    },
    '#leagues': () => {
      currentView = '#leagues';
      renderLeaguesView();
    },
    '#favorites': () => {
      currentView = '#favorites';
      activeFilterLeague = '';
      renderCurrentState();
    }
  };

  new Router(routes);
  startLiveSimulator();
}

document.addEventListener('DOMContentLoaded', initApp);

// Register Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('../sw.js')
      .then(reg => console.log('Service Worker registered successfully.', reg.scope))
      .catch(err => console.error('Service Worker registration failed.', err));
  });
}
