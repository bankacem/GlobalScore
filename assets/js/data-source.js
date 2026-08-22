const ESPN_LEAGUES = [
  ['eng.1', 'Premier League', 'الدوري الإنجليزي الممتاز'],
  ['esp.1', 'La Liga', 'الدوري الإسباني'],
  ['uefa.champions', 'UEFA Champions League', 'دوري أبطال أوروبا'],
];

function mapEspnEvent(event, fallbackLeague, fallbackLeagueAr) {
  const competition = event.competitions?.[0] || {};
  const competitors = competition.competitors || [];
  const home = competitors.find(team => team.homeAway === 'home') || competitors[0] || {};
  const away = competitors.find(team => team.homeAway === 'away') || competitors[1] || {};
  const status = competition.status || event.status || {};
  const statusType = status.type || {};
  const statusName = statusType.name || '';
  const mappedStatus = statusName.includes('IN_PROGRESS') ? 'Live' : statusName.includes('FULL_TIME') || statusName.includes('FINAL') ? 'FT' : 'Scheduled';
  const score = `${home.score ?? 0} - ${away.score ?? 0}`;
  const start = event.date ? new Date(event.date) : null;
  return {
    id: event.id,
    league: event.league?.name || fallbackLeague,
    leagueAr: fallbackLeagueAr,
    home: home.team?.displayName || home.team?.shortDisplayName || 'Home',
    homeAr: home.team?.displayName || home.team?.shortDisplayName || 'Home',
    away: away.team?.displayName || away.team?.shortDisplayName || 'Away',
    awayAr: away.team?.displayName || away.team?.shortDisplayName || 'Away',
    homeLogo: home.team?.logo || '⚽',
    awayLogo: away.team?.logo || '⚽',
    score,
    status: mappedStatus,
    minute: status.displayClock || status.clock || 0,
    time: start ? start.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'}) : '--:--',
    day: start ? start.toLocaleDateString('en', {day: '2-digit'}) : '--',
    month: start ? start.toLocaleDateString('en', {month: 'short'}).toUpperCase() : '---',
    dayAr: start ? start.toLocaleDateString('ar', {day: '2-digit'}) : '--',
    monthAr: start ? start.toLocaleDateString('ar', {month: 'short'}) : '---',
    lineups: null,
    stats: [],
    events: [],
    source: 'ESPN',
  };
}

export class DataSource {
  async getLiveMatches() {
    try {
      const response = await fetch('../assets/data/live.json?v=4', { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Unable to load match data:', error);
      return { matches: [], tables: {} };
    }
  }

  async getEspnMatches() {
    const responses = await Promise.allSettled(ESPN_LEAGUES.map(async ([leagueCode, league, leagueAr]) => {
      const response = await fetch(`https://site.api.espn.com/apis/site/v2/sports/soccer/${leagueCode}/scoreboard`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`${leagueCode}: HTTP ${response.status}`);
      const payload = await response.json();
      return (payload.events || []).map(event => mapEspnEvent(event, league, leagueAr));
    }));
    return responses.flatMap(result => result.status === 'fulfilled' ? result.value : []);
  }

  async getContent() {
    try {
      const response = await fetch('../assets/data/content.json?v=4', { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Unable to load editorial content:', error);
      return { fixtures: [], articles: [] };
    }
  }
}
