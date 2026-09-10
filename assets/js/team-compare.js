const lang = window.GLOBAL_LANG || 'en';
const ar = lang === 'ar';
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const labels = ar ? {one:'الفريق الأول',two:'الفريق الثاني',compare:'قارن الآن',loading:'جاري تحميل النتائج…',played:'مباريات',wins:'فوز',draws:'تعادل',losses:'خسارة',gf:'له',ga:'عليه',points:'نقاط',form:'آخر النتائج',source:'المصدر: لقطة GlobalScore المحلية'} : {one:'Team one',two:'Team two',compare:'Compare now',loading:'Loading match history…',played:'Played',wins:'Wins',draws:'Draws',losses:'Losses',gf:'Goals for',ga:'Goals against',points:'Points',form:'Recent form',source:'Source: GlobalScore local snapshot'};
const formScore = status => status === 'W' ? 'W' : status === 'D' ? 'D' : 'L';
const main = document.getElementById('teamCompare');
const oneSelect = document.getElementById('compareTeamOne');
const twoSelect = document.getElementById('compareTeamTwo');
const cards = [document.getElementById('teamCompareCardOne'), document.getElementById('teamCompareCardTwo')];
let teams = {};

function aggregate(matches) {
  const result = {};
  const ensure = name => result[name] ||= {name, played:0,wins:0,draws:0,losses:0,gf:0,ga:0,points:0,form:[],logo:''};
  matches.filter(m => m.status === 'FT' && m.score && !m.score.includes('—')).forEach(match => {
    const [homeGoals, awayGoals] = match.score.split('-').map(v => Number.parseInt(v.trim(), 10));
    if (!Number.isFinite(homeGoals) || !Number.isFinite(awayGoals)) return;
    const home = ensure(match.home); const away = ensure(match.away); home.logo ||= match.homeLogo; away.logo ||= match.awayLogo;
    home.played++; away.played++; home.gf += homeGoals; home.ga += awayGoals; away.gf += awayGoals; away.ga += homeGoals;
    if (homeGoals > awayGoals) { home.wins++; home.points += 3; away.losses++; home.form.push('W'); away.form.push('L'); }
    else if (homeGoals < awayGoals) { away.wins++; away.points += 3; home.losses++; home.form.push('L'); away.form.push('W'); }
    else { home.draws++; away.draws++; home.points++; away.points++; home.form.push('D'); away.form.push('D'); }
  });
  return result;
}
function option(team) { return `<option value="${esc(team.name)}">${esc(team.name)}</option>`; }
function card(team) { const metrics = [[labels.played,team.played],[labels.wins,team.wins],[labels.draws,team.draws],[labels.losses,team.losses],[labels.gf,team.gf],[labels.ga,team.ga],[labels.points,team.points]]; return `<div class="team-compare-head">${team.logo?.startsWith('http') ? `<img src="${esc(team.logo)}" alt="">` : '<span>⚽</span>'}<h2>${esc(team.name)}</h2></div><div class="team-compare-kpis">${metrics.map(([label,value]) => `<div><strong>${value}</strong><small>${label}</small></div>`).join('')}</div><div class="team-form"><strong>${labels.form}</strong><span>${team.form.slice(-5).map(item => `<i class="form-${item.toLowerCase()}">${item}</i>`).join('') || '—'}</span></div>`; }
function render() { const selected = [teams[oneSelect.value], teams[twoSelect.value]]; cards.forEach((node,i) => { if (node && selected[i]) node.innerHTML = card(selected[i]); }); document.getElementById('teamCompareStatus').textContent = `${labels.source} · ${selected[0]?.played || 0} / ${selected[1]?.played || 0} ${labels.played.toLowerCase()}`; }
async function init() { try { const response = await fetch('../../assets/data/live.json?v=5', {cache:'no-store'}); const data = await response.json(); teams = aggregate(data.matches || []); const list = Object.values(teams).sort((a,b) => b.points - a.points || b.gf - a.gf); list.forEach(team => { oneSelect.insertAdjacentHTML('beforeend', option(team)); twoSelect.insertAdjacentHTML('beforeend', option(team)); }); if (list[0]) oneSelect.value = list[0].name; if (list[1]) twoSelect.value = list[1].name; oneSelect.addEventListener('change', render); twoSelect.addEventListener('change', render); document.getElementById('teamCompareForm').addEventListener('submit', event => { event.preventDefault(); render(); }); render(); } catch (error) { document.getElementById('teamCompareStatus').textContent = ar ? 'تعذر تحميل بيانات المقارنة.' : 'Comparison data is unavailable.'; } }
init();
