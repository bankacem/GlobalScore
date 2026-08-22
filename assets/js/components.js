import { isFavorite, toggleFavorite } from './utils.js';

/**
 * Premium Match Row component
 * @param {Object} match - Match details
 * @param {Function} onClick - Handler for row clicks
 * @returns {HTMLElement}
 */
export function MatchComponent(match, onClick) {
  const div = document.createElement('div');
  div.className = 'match-card';
  if (match.status === 'Live') {
    div.classList.add('live-border');
  }

  const isAr = document.documentElement.lang === 'ar';
  const homeTeam = isAr ? match.homeAr : match.home;
  const awayTeam = isAr ? match.awayAr : match.away;

  let statusText = match.status;
  if (match.status === 'Live') {
    statusText = isAr ? `مباشر ${match.minute}'` : `Live ${match.minute}'`;
  } else if (match.status === 'FT') {
    statusText = isAr ? 'انتهت' : 'FT';
  } else if (match.status === 'HT') {
    statusText = isAr ? 'استراحة' : 'HT';
  } else if (match.status === 'Scheduled') {
    statusText = match.time;
  }

  const starChar = isFavorite(match.id) ? '★' : '☆';

  div.innerHTML = `
    <div class="match-info-section" style="flex: 1; display: flex; align-items: center; justify-content: space-between;">
      <div class="team-side home-side">
        <span class="team-logo">${match.homeLogo}</span>
        <span class="team-name">${homeTeam}</span>
      </div>

      <div class="score-display">
        ${match.status !== 'Scheduled' ? `<span class="score-num">${match.score}</span>` : `<span class="match-time">${match.time}</span>`}
        <span class="status-badge ${match.status === 'Live' ? 'live-pulse' : ''}">${statusText}</span>
      </div>

      <div class="team-side away-side">
        <span class="team-name">${awayTeam}</span>
        <span class="team-logo">${match.awayLogo}</span>
      </div>
    </div>
    <div class="match-actions">
      <button class="fav-btn ${isFavorite(match.id) ? 'active' : ''}" aria-label="${isAr ? 'إضافة المباراة إلى المفضلة' : 'Add match to favorites'}">${starChar}</button>
    </div>
  `;

  // Prevent row click when clicking favorite button
  const favBtn = div.querySelector('.fav-btn');
  favBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    const updated = toggleFavorite(match.id);
    favBtn.textContent = updated ? '★' : '☆';
    favBtn.classList.toggle('active', updated);
  });

  // Handle standard click to show detailed statistics modal
  div.addEventListener('click', onClick);

  return div;
}

/**
 * Reusable League Standings Table Component
 * @param {Array} rows - List of team stats
 * @returns {HTMLElement}
 */
export function LeagueTableComponent(rows) {
  const isAr = document.documentElement.lang === 'ar';
  const table = document.createElement('div');
  table.className = 'table-container';

  table.innerHTML = `
    <table class="standing-table">
      <thead>
        <tr>
          <th>#</th>
          <th style="text-align: left;">${isAr ? 'الفريق' : 'Team'}</th>
          <th>${isAr ? 'لعب' : 'PL'}</th>
          <th>${isAr ? 'فوز' : 'W'}</th>
          <th>${isAr ? 'تعادل' : 'D'}</th>
          <th>${isAr ? 'خسر' : 'L'}</th>
          <th>${isAr ? 'نقاط' : 'PTS'}</th>
          <th class="hide-mobile">${isAr ? 'النموذج' : 'Form'}</th>
        </tr>
      </thead>
      <tbody>
        ${rows.map(row => `
          <tr>
            <td><strong>${row.pos}</strong></td>
            <td style="text-align: left; font-weight: 600;">${isAr ? row.teamAr : row.team}</td>
            <td>${row.p}</td>
            <td>${row.w}</td>
            <td>${row.d}</td>
            <td>${row.l}</td>
            <td><strong class="highlight-pts">${row.pts}</strong></td>
            <td class="form-list hide-mobile">${row.form}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;

  return table;
}

/**
 * Premium Match Detail Dialog View (Modal)
 * @param {Object} match - Match stats details
 * @param {Function} onFavChange - Hook after adding/removing favorites
 * @returns {HTMLElement}
 */
export function MatchDetailModalComponent(match, onFavChange) {
  const isAr = document.documentElement.lang === 'ar';
  const modal = document.createElement('div');
  modal.id = 'matchDetailsModal';
  modal.className = 'modal-backdrop';

  const homeTeam = isAr ? match.homeAr : match.home;
  const awayTeam = isAr ? match.awayAr : match.away;
  const leagueName = isAr ? match.leagueAr : match.league;

  modal.innerHTML = `
    <div class="modal-card">
      <div class="modal-header">
        <span class="modal-title">🏆 ${leagueName}</span>
        <button id="closeModal" class="close-btn" aria-label="${isAr ? 'إغلاق النافذة' : 'Close modal'}">&times;</button>
      </div>

      <div class="modal-body">
        <!-- Live Team header info -->
        <div class="modal-score-header">
          <div class="modal-team">
            <span class="modal-logo">${match.homeLogo}</span>
            <h4>${homeTeam}</h4>
          </div>
          <div class="modal-center">
            <div class="modal-score">${match.status !== 'Scheduled' ? match.score : 'VS'}</div>
            <span class="modal-status">${match.status === 'Live' ? `${match.minute}'` : match.status === 'FT' ? (isAr ? 'انتهت' : 'FT') : (isAr ? 'مجدولة' : 'Scheduled')}</span>
          </div>
          <div class="modal-team">
            <span class="modal-logo">${match.awayLogo}</span>
            <h4>${awayTeam}</h4>
          </div>
        </div>

        <!-- Custom tabs within modal -->
        <div class="modal-tabs">
          <button class="tab-btn active" data-tab="timeline">${isAr ? 'الأحداث' : 'Timeline'}</button>
          <button class="tab-btn" data-tab="stats">${isAr ? 'الإحصائيات' : 'Stats'}</button>
          <button class="tab-btn" data-tab="lineups">${isAr ? 'التشكيلة' : 'Lineups'}</button>
        </div>

        <div class="tab-contents">
          <!-- Timeline Tab -->
          <div id="tab-timeline" class="tab-panel active">
            ${match.events && match.events.length > 0 ? `
              <div class="timeline-list">
                ${match.events.map(ev => `
                  <div class="timeline-item">
                    <span class="time-pin">${ev.minute}'</span>
                    <span class="event-desc">⚽ ${isAr ? ev.playerAr : ev.player} (${isAr ? ev.typeAr : ev.type}) - ${ev.score}</span>
                  </div>
                `).join('')}
              </div>
            ` : `<div class="empty-state">${isAr ? 'لا توجد أحداث بعد.' : 'No events recorded yet.'}</div>`}
          </div>

          <!-- Stats Tab -->
          <div id="tab-stats" class="tab-panel">
            ${match.stats && match.stats.length > 0 ? `
              <div class="stats-list">
                ${match.stats.map(st => `
                  <div class="stat-row">
                    <span class="stat-value">${st.home}</span>
                    <span class="stat-label">${isAr ? st.nameAr : st.name}</span>
                    <span class="stat-value">${st.away}</span>
                  </div>
                  <div class="stat-bar-container">
                    <div class="stat-bar home-bar" style="width: ${st.home}"></div>
                    <div class="stat-bar away-bar" style="width: ${st.away}"></div>
                  </div>
                `).join('')}
              </div>
            ` : `<div class="empty-state">${isAr ? 'الإحصائيات غير متوفرة لهذه المباراة حالياً.' : 'Statistics not available for this match yet.'}</div>`}
          </div>

          <!-- Lineups Tab -->
          <div id="tab-lineups" class="tab-panel">
            ${match.lineups ? `
              <div class="lineup-grid">
                <div class="lineup-column">
                  <h5>${homeTeam}</h5>
                  <ul>
                    ${match.lineups.home.map(p => `<li>🏃‍♂️ ${p}</li>`).join('')}
                  </ul>
                </div>
                <div class="lineup-column">
                  <h5>${awayTeam}</h5>
                  <ul>
                    ${match.lineups.away.map(p => `<li>🏃‍♂️ ${p}</li>`).join('')}
                  </ul>
                </div>
              </div>
            ` : `<div class="empty-state">${isAr ? 'لم يتم الإعلان عن التشكيلة بعد.' : 'Lineups have not been announced yet.'}</div>`}
          </div>
        </div>
      </div>
    </div>
  `;

  // Bind close modal event handler
  modal.querySelector('#closeModal').addEventListener('click', () => {
    modal.remove();
  });

  // Handle backdrop click to close
  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.remove();
  });

  // Bind tabs trigger
  const tabBtns = modal.querySelectorAll('.tab-btn');
  const panels = modal.querySelectorAll('.tab-panel');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      panels.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetId = `tab-${btn.dataset.tab}`;
      modal.querySelector(`#${targetId}`).classList.add('active');
    });
  });

  return modal;
}

/**
 * Toast / Goal alert banner
 * @param {String} title
 * @param {String} subtitle
 */
export function ToastNotification(title, subtitle) {
  const toast = document.createElement('div');
  toast.className = 'goal-toast';
  toast.innerHTML = `
    <div class="toast-body">
      <strong>${title}</strong>
      <span>${subtitle}</span>
    </div>
  `;
  document.body.appendChild(toast);

  // Play browser subtle chime or alert if possible
  try {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.frequency.setValueAtTime(587.33, audioCtx.currentTime); // D5 note
    gain.gain.setValueAtTime(0.05, audioCtx.currentTime);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.3);
  } catch(e) {}

  // Fade out
  setTimeout(() => {
    toast.classList.add('fade-out');
    setTimeout(() => toast.remove(), 500);
  }, 4000);
}
