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
 * Query parameter extractor
 */
export function getQueryParam(param) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(param);
}
