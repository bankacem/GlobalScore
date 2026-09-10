/**
 * Theme Manager Utility
 */
export function setupTheme() {
  const themeToggle = document.getElementById('themeToggle');
  if (!themeToggle) return;

  const currentTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', currentTheme);
  updateThemeButton(themeToggle, currentTheme);

  themeToggle.addEventListener('click', () => {
    const theme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    updateThemeButton(themeToggle, theme);
  });
}

function updateThemeButton(btn, theme) {
  const isAr = document.documentElement.lang === 'ar';
  if (theme === 'dark') {
    btn.textContent = '☀️';
    btn.setAttribute('aria-label', isAr ? 'تبديل المظهر النهاري' : 'Switch to light mode');
  } else {
    btn.textContent = '🌙';
    btn.setAttribute('aria-label', isAr ? 'تبديل المظهر الليلي' : 'Switch to dark mode');
  }
}

/**
 * Language Switcher Utility
 */
export function setupLanguageToggle() {
  const langToggle = document.getElementById('langToggle');
  if (!langToggle) return;

  langToggle.addEventListener('click', () => {
    const currentLang = document.documentElement.lang;
    if (currentLang === 'en') {
      window.location.href = '../ar/';
    } else {
      window.location.href = '../en/';
    }
  });
}

/**
 * Favorites LocalStorage System Helpers
 */
export function getFavorites() {
  const favs = localStorage.getItem('favorites');
  return favs ? JSON.parse(favs) : [];
}

export function isFavorite(id) {
  const favs = getFavorites();
  return favs.includes(Number(id));
}

export function toggleFavorite(id) {
  const numId = Number(id);
  let favs = getFavorites();
  if (favs.includes(numId)) {
    favs = favs.filter(item => item !== numId);
  } else {
    favs.push(numId);
  }
  localStorage.setItem('favorites', JSON.stringify(favs));
  return favs.includes(numId);
}

export async function requestNotifications() {
  if (!('Notification' in window)) return 'unsupported';
  if (Notification.permission === 'default') return Notification.requestPermission();
  return Notification.permission;
}

/**
 * Query parameter extractor
 */
export function getQueryParam(param) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(param);
}
