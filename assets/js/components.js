import { isFavorite, toggleFavorite } from './utils.js';

const esc = (value) => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const badge = (value) => value && String(value).startsWith('http') ? `<img class="team-badge" src="${esc(value)}" alt="">` : `<span>${esc(value || '⚽')}</span>`;

export function MatchComponent(match, onClick) {
  const div = document.createElement('div');
  div.className = `match-card${match.status === 'Live' ? ' live-border' : ''}`;
  const isAr = document.documentElement.lang === 'ar';
  const homeTeam = esc(isAr ? match.homeAr : match.home);
  const awayTeam = esc(isAr ? match.awayAr : match.away);
  let statusText = esc(match.status);
  if (match.status === 'Live') statusText = isAr ? `مباشر ${esc(match.minute)}'` : `Live ${esc(match.minute)}'`;
  else if (match.status === 'FT') statusText = isAr ? 'انتهت' : 'FT';
  else if (match.status === 'HT') statusText = isAr ? 'استراحة' : 'HT';
  else if (match.status === 'Scheduled') statusText = isAr ? 'مجدولة' : 'Scheduled';
  const favorite = isFavorite(match.id);
  div.innerHTML = `
    <div class="match-info-section">
      <div class="team-side home-side"><span class="team-logo">${badge(match.homeLogo)}</span><span class="team-name" title="${homeTeam}">${homeTeam}</span></div>
      <div class="score-display">${match.status !== 'Scheduled' ? `<span class="score-num">${esc(match.score)}</span>` : `<span class="match-time">${esc(match.time)}</span>`}<span class="status-badge ${match.status === 'Live' ? 'live-pulse' : ''}">${statusText}</span></div>
      <div class="team-side away-side"><span class="team-name" title="${awayTeam}">${awayTeam}</span><span class="team-logo">${badge(match.awayLogo)}</span></div>
    </div>
    <div class="match-actions"><button class="fav-btn ${favorite ? 'active' : ''}" aria-label="${isAr ? 'إضافة المباراة إلى المفضلة' : 'Add match to favorites'}">${favorite ? '★' : '☆'}</button></div>`;
  div.querySelector('.fav-btn').addEventListener('click', event => {
    event.stopPropagation();
    const active = toggleFavorite(match.id);
    event.currentTarget.textContent = active ? '★' : '☆';
    event.currentTarget.classList.toggle('active', active);
  });
  div.addEventListener('click', onClick);
  return div;
}

export function LeagueTableComponent(rows, options = {}) {
  const isAr = document.documentElement.lang === 'ar';
  const table = document.createElement('div');
  table.className = 'table-container standings-live-table';
  const logo = row => row.logo && String(row.logo).startsWith('http') ? `<img class="standing-logo" src="${esc(row.logo)}" alt="">` : '';
  table.innerHTML = `<table class="standing-table"><thead><tr><th>#</th><th style="text-align:left">${isAr ? 'الفريق' : 'Team'}</th><th>${isAr ? 'لعب' : 'PL'}</th><th>${isAr ? 'فوز' : 'W'}</th><th>${isAr ? 'تعادل' : 'D'}</th><th>${isAr ? 'خسر' : 'L'}</th><th class="hide-mobile">${isAr ? 'له' : 'GF'}</th><th class="hide-mobile">${isAr ? 'عليه' : 'GA'}</th><th class="hide-mobile">${isAr ? 'الفارق' : 'GD'}</th><th>${isAr ? 'نقاط' : 'PTS'}</th><th class="hide-mobile">${isAr ? 'النموذج' : 'Form'}</th></tr></thead><tbody>${rows.map(row => `<tr><td><strong>${esc(row.pos)}</strong></td><td class="standing-team"><span>${logo(row)}</span><strong title="${esc(isAr ? row.teamAr : row.team)}">${esc(isAr ? row.teamAr : row.team)}</strong></td><td>${esc(row.p)}</td><td>${esc(row.w)}</td><td>${esc(row.d)}</td><td>${esc(row.l)}</td><td class="hide-mobile">${esc(row.gf || '—')}</td><td class="hide-mobile">${esc(row.ga || '—')}</td><td class="hide-mobile">${esc(row.gd || '—')}</td><td><strong class="highlight-pts">${esc(row.pts)}</strong></td><td class="form-list hide-mobile">${esc(row.form || '—')}</td></tr>`).join('')}</tbody></table>`;
  return table;
}

export function MatchDetailModalComponent(match, onFavChange) {
  const isAr = document.documentElement.lang === 'ar';
  const detail = match.details || {};
  const homeTeam = esc(isAr ? match.homeAr : match.home);
  const awayTeam = esc(isAr ? match.awayAr : match.away);
  const leagueName = esc(isAr ? match.leagueAr : match.league);
  const permanentMatchUrl = `matches/${encodeURIComponent(match.id)}.html`;
  const permanentMatchLabel = isAr ? 'فتح صفحة المباراة الدائمة' : 'Open permanent match center';
  const events = detail.events?.length ? detail.events : (match.events || []);
  const rosters = detail.rosters || [];
  const stats = detail.stats || [];
  const statMap = new Map();
  stats.forEach(section => (section.values || []).forEach(stat => {
    const key = stat.name || stat.label;
    if (!statMap.has(key)) statMap.set(key, { label: stat.label || stat.name, teams: [] });
    statMap.get(key).teams.push({ team: section.team, value: stat.value });
  }));
  const statRows = [...statMap.values()];
  const comparisonMarkup = statRows.map(stat => {
    const first = stat.teams[0] || {};
    const second = stat.teams[1] || {};
    const firstNumber = Number.parseFloat(String(first.value ?? '').replace(/[^0-9.]/g, '')) || 0;
    const secondNumber = Number.parseFloat(String(second.value ?? '').replace(/[^0-9.]/g, '')) || 0;
    const total = firstNumber + secondNumber;
    const firstWidth = total ? Math.round(firstNumber / total * 100) : 50;
    return `<div class="comparison-row"><div class="comparison-values"><strong>${esc(first.value || '—')}</strong><span>${esc(stat.label)}</span><strong>${esc(second.value || '—')}</strong></div><div class="comparison-bars"><span class="comparison-bar home-comparison" style="width:${firstWidth}%"></span><span class="comparison-bar away-comparison" style="width:${100 - firstWidth}%"></span></div><div class="comparison-teams"><small>${esc(first.team || homeTeam)}</small><small>${esc(second.team || awayTeam)}</small></div></div>`;
  }).join('');
  const venue = detail.venue ? `${esc(detail.venue)}${detail.city ? ` · ${esc(detail.city)}` : ''}` : (isAr ? 'معلومات الملعب غير متاحة حالياً' : 'Venue information is not available yet');
  const referee = detail.officials?.length ? detail.officials.map(esc).join('، ') : (isAr ? 'لم يُعلن بعد' : 'Not announced yet');
  const attendance = detail.attendance ? `${esc(detail.attendance.toLocaleString?.() || detail.attendance)}` : '—';
  const modal = document.createElement('div');
  modal.id = 'matchDetailsModal';
  modal.className = 'modal-backdrop';
  modal.innerHTML = `
    <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="match-modal-title">
      <div class="modal-header"><span class="modal-title" id="match-modal-title">🏆 ${leagueName}</span><button id="closeModal" class="close-btn" aria-label="${isAr ? 'إغلاق النافذة' : 'Close modal'}">&times;</button></div>
      <div class="modal-body">
        <div class="modal-score-header"><div class="modal-team"><span class="modal-logo">${badge(match.homeLogo)}</span><h4>${homeTeam}</h4></div><div class="modal-center"><div class="modal-score">${match.status !== 'Scheduled' ? esc(match.score) : 'VS'}</div><span class="modal-status">${match.status === 'Live' ? `${isAr ? 'مباشر' : 'Live'} ${esc(match.minute)}'` : match.status === 'FT' ? (isAr ? 'انتهت' : 'FT') : (isAr ? 'مجدولة' : 'Scheduled')}</span></div><div class="modal-team"><span class="modal-logo">${badge(match.awayLogo)}</span><h4>${awayTeam}</h4></div></div>
        <div class="match-meta-grid"><div class="match-meta-item"><span>⚖️</span><div><small>${isAr ? 'الحكم' : 'Referee'}</small><strong>${referee}</strong></div></div><div class="match-meta-item"><span>🏟️</span><div><small>${isAr ? 'الملعب' : 'Venue'}</small><strong>${venue}</strong>${detail.mapUrl ? `<a href="${esc(detail.mapUrl)}" target="_blank" rel="noopener noreferrer">${isAr ? 'فتح الموقع على الخريطة' : 'Open map location'}</a>` : ''}</div></div><div class="match-meta-item"><span>👥</span><div><small>${isAr ? 'الحضور' : 'Attendance'}</small><strong>${attendance}</strong></div></div></div>
        <div class="modal-permanent-action"><a class="primary-btn" href="${permanentMatchUrl}">${permanentMatchLabel} <span>→</span></a></div>
        <div class="modal-tabs"><button class="tab-btn active" data-tab="timeline">${isAr ? 'الأحداث' : 'Events'}</button><button class="tab-btn" data-tab="stats">${isAr ? 'الإحصائيات' : 'Stats'}</button><button class="tab-btn" data-tab="lineups">${isAr ? 'اللاعبون والتشكيلة' : 'Players & lineups'}</button></div>
        <div class="tab-contents">
          <div id="tab-timeline" class="tab-panel active">${events.length ? `<div class="timeline-list">${events.map(event => `<div class="timeline-item"><span class="time-pin">${esc(event.minute)}'</span><span class="event-desc">${esc(event.text)}</span></div>`).join('')}</div>` : `<div class="empty-state">${isAr ? 'لا توجد أحداث منشورة بعد.' : 'No match events have been published yet.'}</div>`}</div>
          <div id="tab-stats" class="tab-panel">${statRows.length ? `<div class="comparison-list">${comparisonMarkup}</div>` : `<div class="empty-state">${isAr ? 'الإحصائيات غير متوفرة لهذه المباراة حالياً.' : 'Statistics are not available for this match yet.'}</div>`}</div>
          <div id="tab-lineups" class="tab-panel">${rosters.length ? `<div class="lineup-grid">${rosters.map(roster => `<div class="lineup-column"><h5>${esc(roster.team)} ${roster.formation ? `<small>${esc(roster.formation)}</small>` : ''}</h5><ul>${roster.players.map(player => `<li><span>${esc(player.name)}</span><small>${player.starter ? (isAr ? 'أساسي' : 'XI') : (isAr ? 'بديل' : 'Sub')}${player.position ? ` · ${esc(player.position)}` : ''}${player.jersey ? ` · #${esc(player.jersey)}` : ''}</small></li>`).join('')}</ul></div>`).join('')}</div>` : `<div class="empty-state">${isAr ? 'لم يتم الإعلان عن التشكيلة بعد.' : 'Lineups have not been announced yet.'}</div>`}</div>
        </div>
      </div>
    </div>`;
  modal.querySelector('#closeModal').addEventListener('click', () => modal.remove());
  modal.addEventListener('click', event => { if (event.target === modal) modal.remove(); });
  modal.querySelectorAll('.tab-btn').forEach(button => button.addEventListener('click', () => {
    modal.querySelectorAll('.tab-btn').forEach(item => item.classList.remove('active'));
    modal.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
    button.classList.add('active');
    modal.querySelector(`#tab-${button.dataset.tab}`).classList.add('active');
  }));
  return modal;
}

export function ToastNotification(title, subtitle) {
  const toast = document.createElement('div');
  toast.className = 'goal-toast';
  toast.innerHTML = `<div class="toast-body"><strong>${esc(title)}</strong><span>${esc(subtitle)}</span></div>`;
  document.body.appendChild(toast);
  setTimeout(() => { toast.classList.add('fade-out'); setTimeout(() => toast.remove(), 500); }, 4000);
}
