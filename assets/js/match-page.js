const MATCH = window.GLOBAL_MATCH || {};
const LANG = window.GLOBAL_LANG || 'en';
const AR = LANG === 'ar';
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const copy = {
  en: { live: 'Live', ft: 'FT', scheduled: 'Scheduled', notAvailable: 'Not available yet', noEvents: 'No published events yet.', noStats: 'Statistics are not available yet.', noLineups: 'Line-ups have not been announced yet.', home: 'Home', away: 'Away', starter: 'XI', sub: 'Sub', referee: 'Referee', venue: 'Venue', attendance: 'Attendance', updated: 'Updated just now' },
  ar: { live: 'مباشر', ft: 'انتهت', scheduled: 'مجدولة', notAvailable: 'غير متاح حالياً', noEvents: 'لا توجد أحداث منشورة بعد.', noStats: 'الإحصائيات غير متوفرة بعد.', noLineups: 'لم يتم الإعلان عن التشكيلات بعد.', home: 'صاحب الأرض', away: 'الضيف', starter: 'أساسي', sub: 'بديل', referee: 'الحكم', venue: 'الملعب', attendance: 'الحضور', updated: 'تم التحديث الآن' },
  fr: { live: 'En direct', ft: 'Terminé', scheduled: 'Programmé', notAvailable: 'Pas encore disponible', noEvents: 'Aucun événement publié pour le moment.', noStats: 'Les statistiques ne sont pas encore disponibles.', noLineups: 'Les compositions ne sont pas encore annoncées.', home: 'Domicile', away: 'Extérieur', starter: 'Titulaire', sub: 'Remplaçant', referee: 'Arbitre', venue: 'Stade', attendance: 'Affluence', updated: 'Mis à jour à l’instant' },
  es: { live: 'En directo', ft: 'Finalizado', scheduled: 'Programado', notAvailable: 'Todavía no disponible', noEvents: 'Todavía no hay acontecimientos publicados.', noStats: 'Las estadísticas todavía no están disponibles.', noLineups: 'Las alineaciones todavía no han sido anunciadas.', home: 'Local', away: 'Visitante', starter: 'Titular', sub: 'Suplente', referee: 'Árbitro', venue: 'Estadio', attendance: 'Asistencia', updated: 'Actualizado ahora' },
}[LANG] || {};

function statusLabel(status, minute) {
  if (status === 'Live') return `${copy.live} ${minute || ''}`.trim();
  if (status === 'FT') return copy.ft;
  return copy.scheduled;
}

function mapStatus(type) {
  const name = type?.name || '';
  if (name.includes('IN_PROGRESS') || name.includes('HALFTIME') || name.includes('END_PERIOD')) return 'Live';
  if (name.includes('FULL_TIME') || name.includes('FINAL')) return 'FT';
  return 'Scheduled';
}

function numberValue(value) {
  return Number.parseFloat(String(value ?? '').replace(/[^0-9.]/g, '')) || 0;
}

function renderEvents(events) {
  const target = document.getElementById('match-events');
  if (!target) return;
  if (!events.length) {
    target.className = 'permanent-empty';
    target.textContent = copy.noEvents;
    return;
  }
  target.className = 'permanent-event-list';
  target.innerHTML = events.map(event => `<div class="permanent-event-item"><strong>${esc(event.minute || '—')}${event.minute ? "'" : ''}</strong><span>${esc(event.text || event.type || '')}</span></div>`).join('');
}

function renderStats(stats) {
  const target = document.getElementById('match-stats');
  if (!target) return;
  const map = new Map();
  stats.forEach(section => (section.statistics || section.values || []).forEach(stat => {
    const key = stat.name || stat.label || '';
    if (!key) return;
    if (!map.has(key)) map.set(key, { label: stat.label || stat.name, teams: [] });
    map.get(key).teams.push({ team: section.team || '', value: stat.displayValue ?? stat.value ?? '' });
  }));
  const rows = [...map.values()];
  if (!rows.length) {
    target.className = 'permanent-empty';
    target.textContent = copy.noStats;
    return;
  }
  target.className = 'permanent-stat-list';
  target.innerHTML = rows.map(row => {
    const first = row.teams[0] || {};
    const second = row.teams[1] || {};
    const firstNumber = numberValue(first.value);
    const secondNumber = numberValue(second.value);
    const total = firstNumber + secondNumber;
    const width = total ? Math.round(firstNumber / total * 100) : 50;
    return `<div class="permanent-stat-row"><div class="permanent-stat-values"><strong>${esc(first.value || '—')}</strong><span>${esc(row.label)}</span><strong>${esc(second.value || '—')}</strong></div><div class="permanent-stat-bars"><span style="width:${width}%"></span><span style="width:${100 - width}%"></span></div><div class="permanent-stat-teams"><small>${esc(first.team || MATCH.home)}</small><small>${esc(second.team || MATCH.away)}</small></div></div>`;
  }).join('');
}

function renderLineups(rosters) {
  const target = document.getElementById('match-lineups');
  if (!target) return;
  if (!rosters.length) {
    target.className = 'permanent-empty';
    target.textContent = copy.noLineups;
    return;
  }
  target.className = 'permanent-lineup-grid';
  target.innerHTML = rosters.map(roster => `<section class="permanent-lineup-column"><h3>${esc(roster.team)}${roster.formation ? `<small>${esc(roster.formation)}</small>` : ''}</h3><ul>${(roster.players || []).map(player => `<li><span>${esc(player.name)}</span><small>${player.starter ? copy.starter : copy.sub}${player.position ? ` · ${esc(player.position)}` : ''}${player.jersey ? ` · #${esc(player.jersey)}` : ''}</small></li>`).join('')}</ul></section>`).join('');
}

function applySummary(payload) {
  const competition = payload.header?.competitions?.[0] || payload.competitions?.[0] || {};
  const competitors = competition.competitors || [];
  const home = competitors.find(item => item.homeAway === 'home') || competitors[0] || {};
  const away = competitors.find(item => item.homeAway === 'away') || competitors[1] || {};
  const type = competition.status?.type || {};
  const status = mapStatus(type);
  const minute = type.shortDetail || competition.status?.displayClock || '';
  const score = `${home.score ?? 0} - ${away.score ?? 0}`;
  const scoreNode = document.getElementById('match-score');
  const statusNode = document.getElementById('match-status');
  const minuteNode = document.getElementById('match-minute');
  if (scoreNode) scoreNode.textContent = score;
  if (statusNode) statusNode.textContent = statusLabel(status, minute);
  if (minuteNode) minuteNode.textContent = status === 'Live' ? minute : '';
  const info = payload.gameInfo || {};
  const venue = info.venue || {};
  const address = venue.address || {};
  const referee = (info.officials || []).map(item => item.fullName || item.displayName).filter(Boolean).join(AR ? '، ' : ', ');
  const venueText = [venue.fullName || venue.shortName, address.city].filter(Boolean).join(' · ');
  const refereeNode = document.getElementById('match-referee');
  const venueNode = document.getElementById('match-venue');
  const attendanceNode = document.getElementById('match-attendance');
  if (refereeNode) refereeNode.textContent = referee || copy.notAvailable;
  if (venueNode) venueNode.textContent = venueText || copy.notAvailable;
  if (attendanceNode) attendanceNode.textContent = info.attendance ? Number(info.attendance).toLocaleString(LANG) : '—';
  const mapNode = document.getElementById('match-map');
  if (mapNode && venueText) {
    mapNode.href = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(venueText)}`;
    mapNode.classList.remove('is-hidden');
  }
  const events = (payload.keyEvents || []).filter(event => event.type?.type !== 'kickoff').map(event => ({ minute: event.clock?.displayValue || event.period?.displayValue || event.clock?.value || '', text: event.text || event.type?.text || '', type: event.type?.text || '' }));
  const rosters = (payload.rosters || []).map(roster => ({ team: roster.team?.displayName || '', formation: roster.formation?.displayName || roster.formation?.text || '', players: (roster.roster || []).map(item => ({ name: item.athlete?.displayName || item.athlete?.shortName || '', starter: Boolean(item.starter), position: item.position?.abbreviation || item.position?.displayName || '', jersey: item.jersey || '' })).filter(item => item.name) }));
  const stats = (payload.boxscore?.teams || []).map(team => ({ team: team.team?.displayName || '', statistics: team.statistics || [] }));
  renderEvents(events);
  renderStats(stats);
  renderLineups(rosters);
}

async function refreshMatch() {
  if (!MATCH.id || !MATCH.leagueCode) return;
  try {
    const response = await fetch(`https://site.api.espn.com/apis/site/v2/sports/soccer/${encodeURIComponent(MATCH.leagueCode)}/summary?event=${encodeURIComponent(MATCH.id)}`, { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    applySummary(await response.json());
    const note = document.querySelector('.permanent-source-note');
    if (note) note.dataset.updated = copy.updated;
  } catch (error) {
    console.warn('Match center refresh unavailable:', error);
  }
}

refreshMatch();
window.setInterval(refreshMatch, 15000);
