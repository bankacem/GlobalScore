/**
 * Reusable match row component
 * @param {Object} match - Match details
 * @returns {HTMLElement}
 */
export function MatchComponent(match) {
  const div = document.createElement('div');
  div.className = 'match';

  const isAr = document.documentElement.lang === 'ar';
  const homeTeam = isAr ? (match.homeAr || match.home) : match.home;
  const awayTeam = isAr ? (match.awayAr || match.away) : match.away;
  const status = isAr ? (match.statusAr || match.status) : match.status;

  div.innerHTML = `
    <div class="match-team home">${homeTeam}</div>
    <div class="match-score-container">
      <div class="match-score">${match.score}</div>
      <div class="match-status">${status}</div>
    </div>
    <div class="match-team away">${awayTeam}</div>
  `;

  return div;
}
