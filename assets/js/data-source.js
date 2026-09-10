const ESPN_LEAGUES = [
  ['eng.1', 'Premier League', 'الدوري الإنجليزي الممتاز'],
  ['esp.1', 'La Liga', 'الدوري الإسباني'],
  ['uefa.champions', 'UEFA Champions League', 'دوري أبطال أوروبا'],
];

function mapEspnEvent(event, fallbackLeague, fallbackLeagueAr, leagueCode) {
  const competition = event.competitions?.[0] || {};
  const competitors = competition.competitors || [];
  const home = competitors.find(team => team.homeAway === 'home') || competitors[0] || {};
  const away = competitors.find(team => team.homeAway === 'away') || competitors[1] || {};
  const status = competition.status || event.status || {};
  const statusType = status.type || {};
  const statusName = statusType.name || '';
  const mappedStatus = statusName.includes('IN_PROGRESS') ? 'Live' : statusName.includes('FULL_TIME') || statusName.includes('FINAL') ? 'FT' : 'Scheduled';
  const score = `${home.score ?? '—'} - ${away.score ?? '—'}`;
  const start = event.date ? new Date(event.date) : null;
  return {
    id: event.id,
    leagueCode,
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
      return (payload.events || []).map(event => mapEspnEvent(event, league, leagueAr, leagueCode));
    }));
    return responses.flatMap(result => result.status === 'fulfilled' ? result.value : []);
  }

  async getStandings(leagueCode) {
    const league = ESPN_LEAGUES.find(item => item[0] === leagueCode) || [leagueCode, leagueCode, leagueCode];
    try {
      const response = await fetch(`https://site.api.espn.com/apis/v2/sports/soccer/${leagueCode}/standings`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`${leagueCode}: HTTP ${response.status}`);
      const payload = await response.json();
      const groups = (payload.children || []).map(group => ({
        name: group.name || league[1],
        rows: (group.standings?.entries || []).map(entry => {
          const stats = Object.fromEntries((entry.stats || []).map(stat => [stat.name, stat]));
          const value = (...names) => {
            const stat = names.map(name => stats[name]).find(Boolean);
            return stat?.displayValue ?? stat?.value ?? '';
          };
          return {
            pos: value('rank'),
            team: entry.team?.displayName || entry.team?.shortDisplayName || '',
            teamAr: entry.team?.displayName || entry.team?.shortDisplayName || '',
            logo: entry.team?.logos?.[0]?.href || '',
            p: value('gamesPlayed'),
            w: value('wins'),
            d: value('ties', 'draws'),
            l: value('losses'),
            gf: value('goalsFor'),
            ga: value('goalsAgainst'),
            gd: value('pointDifferential', 'goalDifference'),
            pts: value('points'),
            form: value('form', 'streak'),
          };
        }),
      })).filter(group => group.rows.length);
      return { leagueCode, league: league[1], leagueAr: league[2], groups };
    } catch (error) {
      console.warn('Unable to load ESPN standings:', error);
      return { leagueCode, league: league[1], leagueAr: league[2], groups: [] };
    }
  }

  async getAllStandings() {
    const responses = await Promise.all(ESPN_LEAGUES.map(([leagueCode]) => this.getStandings(leagueCode)));
    return responses.filter(item => item.groups.length);
  }

  async getMatchDetails(match) {
    if (!match?.id || !match?.leagueCode) return null;
    try {
      const response = await fetch(`https://site.api.espn.com/apis/site/v2/sports/soccer/${match.leagueCode}/summary?event=${encodeURIComponent(match.id)}`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = await response.json();
      const info = payload.gameInfo || {};
      const venue = info.venue || {};
      const address = venue.address || {};
      const officials = (info.officials || []).map(referee => referee.fullName || referee.displayName).filter(Boolean);
      const rosters = (payload.rosters || []).map(roster => ({
        homeAway: roster.homeAway,
        team: roster.team?.displayName || '',
        formation: roster.formation?.displayName || roster.formation?.text || '',
        players: (roster.roster || []).map(item => ({
          name: item.athlete?.displayName || item.athlete?.shortName || '',
          starter: Boolean(item.starter),
          substitute: Boolean(item.substitute),
          position: item.position?.abbreviation || item.position?.displayName || '',
          jersey: item.jersey || '',
        })).filter(item => item.name),
      }));
      const stats = (payload.boxscore?.teams || []).map(team => ({
        team: team.team?.displayName || '',
        values: (team.statistics || []).map(stat => ({
          name: stat.name || stat.label || '',
          label: stat.label || stat.name || '',
          value: stat.displayValue ?? stat.value ?? '',
        })),
      }));
      const events = (payload.keyEvents || []).filter(event => event.type?.type !== 'kickoff').map(event => ({
        minute: event.clock?.displayValue || event.period?.displayValue || event.clock?.value || '',
        text: event.text || event.type?.text || '',
        type: event.type?.text || '',
      }));
      return {
        venue: venue.fullName || venue.shortName || '',
        city: address.city || '',
        country: address.country || '',
        mapUrl: venue.fullName && address.city ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${venue.fullName}, ${address.city}`)}` : '',
        attendance: info.attendance || '',
        officials,
        rosters,
        stats,
        events,
        summaryUrl: payload.links?.[0]?.href || '',
      };
    } catch (error) {
      console.warn('Unable to load ESPN match details:', error);
      return null;
    }
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
