import { DataSource } from './data-source.js';
import { MatchComponent } from './components.js';
import { setupTheme, setupLanguageToggle, getQueryParam } from './utils.js';

const dataSource = new DataSource();

async function loadLive() {
  const container = document.getElementById('liveMatches');
  if (!container) return;

  const matches = await dataSource.getLiveMatches();
  container.innerHTML = '';

  if (matches.length === 0) {
    const isAr = document.documentElement.lang === 'ar';
    container.innerHTML = `<div class="loading">${isAr ? 'لا توجد مباريات حالياً.' : 'No live matches found.'}</div>`;
    return;
  }

  matches.forEach(match => {
    const matchEl = MatchComponent(match);
    container.appendChild(matchEl);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  // Setup standard features (Theme + Language)
  setupTheme();
  setupLanguageToggle();

  // Load live matches
  loadLive();
});

// Register Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(reg => console.log('Service Worker registered successfully.', reg.scope))
      .catch(err => console.error('Service Worker registration failed.', err));
  });
}
