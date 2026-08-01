// tools/seo-agent-pro/lib/content-en.mjs
import { pick, escapeHtml } from './seo.mjs';

const OPENERS_WIN = [
  (h, a, s) => `${h} got the better of ${a} in a ${s} scoreline that will please their supporters.`,
  (h, a, s) => `A disciplined performance saw ${h} see off ${a}, closing the game out ${s}.`,
  (h, a, s) => `${h} made home advantage count, edging past ${a} ${s} in an entertaining clash.`,
  (h, a, s) => `It finished ${s} in favour of ${h}, who never let ${a} settle into a rhythm.`,
];

const OPENERS_DRAW = [
  (h, a, s) => `${h} and ${a} shared the spoils in a tightly contested ${s} draw.`,
  (h, a, s) => `Neither side could find a winner as ${h} and ${a} played out a ${s} stalemate.`,
  (h, a, s) => `A end-to-end affair between ${h} and ${a} finished level, ${s}.`,
];

const STATS_LEAD = [
  (team, stat) => `${team} dominated territorially, finishing with the edge in ${stat}.`,
  (team, stat) => `Control of the game largely belonged to ${team}, who came out on top in ${stat}.`,
  (team, stat) => `The numbers back up the eye test: ${team} led the way in ${stat}.`,
];

const CLOSERS = [
  (h, a) => `Both sides will now shift focus to their next fixtures as the race in the standings continues.`,
  (h, a) => `Attention turns quickly to the coming rounds, where both ${h} and ${a} will look to build on this display.`,
  (h, a) => `With the schedule showing no signs of slowing down, both clubs head into their next assignment with plenty to work on.`,
];

const PREVIEW_OPENERS = [
  (h, a, l) => `${h} host ${a} in a ${l} fixture that could have a real say in how the table shapes up.`,
  (h, a, l) => `All eyes turn to this ${l} meeting between ${h} and ${a}, two sides with plenty on the line.`,
  (h, a, l) => `${h} welcome ${a} for a ${l} clash that promises to be closely fought from the first whistle.`,
];

function statLine(name, home, away) {
  return `<tr><td>${escapeHtml(name)}</td><td>${escapeHtml(home)}</td><td>${escapeHtml(away)}</td></tr>`;
}

function possessionLeader(stats, home, away) {
  const poss = stats.find((s) => /possession/i.test(s.name));
  if (!poss) return null;
  const h = parseFloat(poss.home);
  const a = parseFloat(poss.away);
  if (Number.isNaN(h) || Number.isNaN(a)) return null;
  return h >= a ? { team: home, value: poss.home } : { team: away, value: poss.away };
}

function eventsTimeline(events, homeAr) {
  if (!events || !events.length) {
    return `<p>The two sides could not find a way through, with clear-cut chances at a premium.</p>`;
  }
  const items = events
    .map((e) => `<li><strong>${e.minute}&rsquo;</strong> — ${escapeHtml(e.player)} ${e.type === 'Goal' ? 'scores' : escapeHtml(e.type).toLowerCase()}, making it ${escapeHtml(e.score)}.</li>`)
    .join('\n');
  return `<ul class="article-timeline">${items}</ul>`;
}

function lineupList(names = []) {
  return `<ol class="article-lineup">${names.map((n) => `<li>${escapeHtml(n)}</li>`).join('')}</ol>`;
}

export function buildEnglishArticle(match) {
  const { home, away, league, score, status, events, stats, lineups } = match;
  const seed = match.id;

  if (status === 'Scheduled') {
    const opener = pick(seed, PREVIEW_OPENERS)(home, away, league);
    const title = `${home} vs ${away} Preview: ${league} Kick-Off Time & Team News`;
    const description = `${home} vs ${away} preview: kick-off time, probable lineups and everything you need to know ahead of this ${league} fixture.`;

    const lineupSection =
      lineups && (lineups.home?.length || lineups.away?.length)
        ? `<h2>Probable Lineups</h2>
           <div class="article-lineups-grid">
             <div><h3>${escapeHtml(home)}</h3>${lineupList(lineups.home)}</div>
             <div><h3>${escapeHtml(away)}</h3>${lineupList(lineups.away)}</div>
           </div>`
        : '';

    const body = `
      <p>${opener}</p>
      <p>Kick-off is scheduled for <strong>${escapeHtml(match.time)}</strong>, with both clubs arriving in this ${escapeHtml(league)} round looking to make an early statement. Expect a cagey opening spell before the game opens up in the second half, as is often the case in fixtures of this magnitude.</p>
      ${lineupSection}
      <h2>How to Follow the Match</h2>
      <p>Live score updates, key moments and full-time stats for ${escapeHtml(home)} vs ${escapeHtml(away)} will be available on GlobalScore as soon as the match kicks off. Bookmark this page and refresh for minute-by-minute coverage.</p>
      <h2>Frequently Asked Questions</h2>
      <p><strong>What time does ${escapeHtml(home)} vs ${escapeHtml(away)} kick off?</strong><br>The match is scheduled for ${escapeHtml(match.time)} local time.</p>
      <p><strong>Where can I follow live updates?</strong><br>GlobalScore will provide live score updates, lineups and match events throughout the game.</p>
    `;
    return { title, description, body, type: 'preview' };
  }

  const isDraw = (() => {
    const [h, a] = score.split('-').map((n) => parseInt(n.trim(), 10));
    return h === a;
  })();

  const opener = isDraw
    ? pick(seed, OPENERS_DRAW)(home, away, score)
    : pick(seed, OPENERS_WIN)(
        (() => {
          const [h, a] = score.split('-').map((n) => parseInt(n.trim(), 10));
          return h > a ? home : away;
        })(),
        (() => {
          const [h, a] = score.split('-').map((n) => parseInt(n.trim(), 10));
          return h > a ? away : home;
        })(),
        score
      );

  const leader = stats ? possessionLeader(stats, home, away) : null;
  const statsLead = leader ? pick(seed + 1, STATS_LEAD)(leader.team, `possession (${leader.value})`) : '';

  const statsTable = stats && stats.length
    ? `<h2>Match Statistics</h2>
       <table class="article-stats-table">
         <thead><tr><th>Stat</th><th>${escapeHtml(home)}</th><th>${escapeHtml(away)}</th></tr></thead>
         <tbody>${stats.map((s) => statLine(s.name, s.home, s.away)).join('\n')}</tbody>
       </table>
       <p>${statsLead}</p>`
    : '';

  const lineupSection =
    lineups && (lineups.home?.length || lineups.away?.length)
      ? `<h2>Starting Lineups</h2>
         <div class="article-lineups-grid">
           <div><h3>${escapeHtml(home)}</h3>${lineupList(lineups.home)}</div>
           <div><h3>${escapeHtml(away)}</h3>${lineupList(lineups.away)}</div>
         </div>`
      : '';

  const statusLabel = status === 'Live' ? `Live — ${match.minute}'` : 'Full-Time';
  const title = status === 'Live'
    ? `${home} ${score} ${away}: Live Updates, Goals & Match Events`
    : `${home} ${score} ${away}: Match Report – ${league}`;
  const description = status === 'Live'
    ? `Follow ${home} vs ${away} live: current score ${score}, goals, key moments and stats updated as the match unfolds.`
    : `${home} ${score} ${away} — full match report with goals, key statistics and lineups from this ${league} clash.`;

  const closer = pick(seed + 2, CLOSERS)(home, away);

  const body = `
    <p class="article-status-badge">${escapeHtml(statusLabel)} · ${escapeHtml(league)}</p>
    <p>${opener} ${statsLead && status === 'FT' ? '' : ''}</p>
    <h2>Key Moments</h2>
    ${eventsTimeline(events)}
    ${statsTable}
    ${lineupSection}
    <h2>${status === 'Live' ? 'What Happens Next' : 'Match Summary'}</h2>
    <p>${closer}</p>
    <h2>Frequently Asked Questions</h2>
    <p><strong>What was the final score between ${escapeHtml(home)} and ${escapeHtml(away)}?</strong><br>${status === 'FT' ? `The match finished ${escapeHtml(score)}.` : `The match is currently in progress with the score at ${escapeHtml(score)}.`}</p>
    <p><strong>Who scored for ${escapeHtml(home)} and ${escapeHtml(away)}?</strong><br>${events && events.length ? `Goals came from ${events.map((e) => e.player).join(', ')}.` : 'Full goal details are listed in the Key Moments section above.'}</p>
  `;

  return { title, description, body, type: status === 'Live' ? 'live' : 'report' };
}
