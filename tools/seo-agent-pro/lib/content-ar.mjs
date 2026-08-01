// tools/seo-agent-pro/lib/content-ar.mjs
import { pick, escapeHtml } from './seo.mjs';

const OPENERS_WIN = [
  (h, a, s) => `فرض ${h} سيطرته على مجريات اللقاء أمام ${a} لينتهي اللقاء بنتيجة ${s} تعيد الابتسامة لجماهيره.`,
  (h, a, s) => `أداء منظم قاد ${h} إلى حسم المواجهة أمام ${a} بنتيجة ${s} بعد لقاء اتسم بالندية في شوطه الأول.`,
  (h, a, s) => `استغل ${h} عامل الأرض والجمهور ليخرج بفوز ثمين على ${a} بنتيجة ${s} في مباراة لم تخلُ من الإثارة.`,
  (h, a, s) => `انتهت المواجهة بنتيجة ${s} لصالح ${h}، الذي لم يمنح ${a} فرصة لفرض إيقاعه على اللقاء.`,
];

const OPENERS_DRAW = [
  (h, a, s) => `تقاسم ${h} و${a} نقاط اللقاء بعد تعادل مثير انتهى بنتيجة ${s}.`,
  (h, a, s) => `لم يستطع أي من الفريقين حسم اللقاء لصالحه، لينتهي الشوطان بتعادل ${s} بين ${h} و${a}.`,
  (h, a, s) => `مباراة مفتوحة بين ${h} و${a} انتهت بالتعادل ${s} دون أن يحسم أي طرف كفة المواجهة.`,
];

const STATS_LEAD = [
  (team, stat) => `سيطر ${team} على مجريات اللعب، وجاء ذلك واضحًا من خلال تفوقه في إحصائية ${stat}.`,
  (team, stat) => `عكست الأرقام ما شهدته أرضية الملعب، إذ تفوق ${team} في إحصائية ${stat}.`,
  (team, stat) => `كانت الكرة في الغالب بحوزة ${team}، الذي تصدّر إحصائية ${stat} خلال اللقاء.`,
];

const CLOSERS = [
  (h, a) => `يتجه الفريقان الآن نحو استحقاقاتهما القادمة في ظل تنافس محتدم على صدارة الترتيب.`,
  (h, a) => `تتحول الأنظار سريعًا نحو الجولات المقبلة، حيث يسعى كل من ${h} و${a} للبناء على هذا الأداء.`,
  (h, a) => `مع استمرار الموسم بوتيرته السريعة، يدخل الناديان مبارياتهما القادمة وأمامهما الكثير للعمل عليه.`,
];

const PREVIEW_OPENERS = [
  (h, a, l) => `يستضيف ${h} نظيره ${a} في مواجهة من ${l} قد يكون لها تأثير مباشر على شكل جدول الترتيب.`,
  (h, a, l) => `تتجه الأنظار نحو هذا اللقاء ضمن ${l} الذي يجمع ${h} و${a}، الفريقين الطامحين لتحقيق نتيجة إيجابية.`,
  (h, a, l) => `يستقبل ${h} ضيفه ${a} في مباراة من ${l} يُتوقع أن تشهد تنافسًا قويًا منذ الصافرة الأولى.`,
];

function statLine(name, home, away) {
  return `<tr><td>${escapeHtml(name)}</td><td>${escapeHtml(home)}</td><td>${escapeHtml(away)}</td></tr>`;
}

function possessionLeader(stats, homeAr, awayAr) {
  const poss = stats.find((s) => /الاستحواذ/.test(s.nameAr || '') || /possession/i.test(s.name || ''));
  if (!poss) return null;
  const h = parseFloat(poss.home);
  const a = parseFloat(poss.away);
  if (Number.isNaN(h) || Number.isNaN(a)) return null;
  return h >= a ? { team: homeAr, value: poss.home } : { team: awayAr, value: poss.away };
}

function eventsTimeline(events) {
  if (!events || !events.length) {
    return `<p>لم يتمكن أي من الفريقين من إيجاد الطريق نحو الشباك، وسط ندرة في الفرص الحقيقية للتهديف.</p>`;
  }
  const items = events
    .map((e) => `<li><strong>د.${e.minute}</strong> — ${escapeHtml(e.playerAr || e.player)} ${e.typeAr === 'هدف' ? 'يسجل هدفًا' : escapeHtml(e.typeAr || e.type)}، لتصبح النتيجة ${escapeHtml(e.score)}.</li>`)
    .join('\n');
  return `<ul class="article-timeline">${items}</ul>`;
}

function lineupList(names = []) {
  return `<ol class="article-lineup">${names.map((n) => `<li>${escapeHtml(n)}</li>`).join('')}</ol>`;
}

export function buildArabicArticle(match) {
  const { home, away, homeAr, awayAr, league, leagueAr, score, status, events, stats, lineups } = match;
  const seed = match.id;
  const hAr = homeAr || home;
  const aAr = awayAr || away;
  const lAr = leagueAr || league;

  if (status === 'Scheduled') {
    const opener = pick(seed, PREVIEW_OPENERS)(hAr, aAr, lAr);
    const title = `${hAr} ضد ${aAr}: موعد المباراة والتشكيل المتوقع – ${lAr}`;
    const description = `كل ما تريد معرفته عن مباراة ${hAr} ضد ${aAr}: موعد الانطلاق، التشكيل المتوقع، وأبرز المعطيات قبل المواجهة ضمن ${lAr}.`;

    const lineupSection =
      lineups && (lineups.home?.length || lineups.away?.length)
        ? `<h2>التشكيل المتوقع</h2>
           <div class="article-lineups-grid">
             <div><h3>${escapeHtml(hAr)}</h3>${lineupList(lineups.home)}</div>
             <div><h3>${escapeHtml(aAr)}</h3>${lineupList(lineups.away)}</div>
           </div>`
        : '';

    const body = `
      <p>${opener}</p>
      <p>من المقرر أن تنطلق المباراة عند الساعة <strong>${escapeHtml(match.time)}</strong>، حيث يدخل الفريقان هذه الجولة من ${escapeHtml(lAr)} بطموح تحقيق نتيجة إيجابية مبكرة. يُتوقع أن تشهد الدقائق الأولى حذرًا تكتيكيًا من الطرفين قبل أن تنفتح المباراة تدريجيًا في الشوط الثاني.</p>
      ${lineupSection}
      <h2>كيف تتابع المباراة</h2>
      <p>ستتوفر تحديثات النتيجة لحظة بلحظة، وأبرز الأحداث والإحصائيات الكاملة لمباراة ${escapeHtml(hAr)} ضد ${escapeHtml(aAr)} عبر موقع GlobalScore فور انطلاق صافرة البداية.</p>
      <h2>أسئلة شائعة</h2>
      <p><strong>متى تنطلق مباراة ${escapeHtml(hAr)} وأما ${escapeHtml(aAr)}؟</strong><br>موعد الانطلاق المقرر هو ${escapeHtml(match.time)} بالتوقيت المحلي.</p>
      <p><strong>أين يمكنني متابعة التحديثات الحية؟</strong><br>يوفر موقع GlobalScore تحديثات مباشرة للنتيجة والتشكيلة وأبرز الأحداث طوال زمن المباراة.</p>
    `;
    return { title, description, body, type: 'preview' };
  }

  const isDraw = (() => {
    const [h, a] = score.split('-').map((n) => parseInt(n.trim(), 10));
    return h === a;
  })();

  const opener = isDraw
    ? pick(seed, OPENERS_DRAW)(hAr, aAr, score)
    : pick(seed, OPENERS_WIN)(
        (() => {
          const [h, a] = score.split('-').map((n) => parseInt(n.trim(), 10));
          return h > a ? hAr : aAr;
        })(),
        (() => {
          const [h, a] = score.split('-').map((n) => parseInt(n.trim(), 10));
          return h > a ? aAr : hAr;
        })(),
        score
      );

  const leader = stats ? possessionLeader(stats, hAr, aAr) : null;
  const statsLead = leader ? pick(seed + 1, STATS_LEAD)(leader.team, `الاستحواذ (${leader.value})`) : '';

  const statsTable = stats && stats.length
    ? `<h2>إحصائيات المباراة</h2>
       <table class="article-stats-table">
         <thead><tr><th>الإحصائية</th><th>${escapeHtml(hAr)}</th><th>${escapeHtml(aAr)}</th></tr></thead>
         <tbody>${stats.map((s) => statLine(s.nameAr || s.name, s.home, s.away)).join('\n')}</tbody>
       </table>
       <p>${statsLead}</p>`
    : '';

  const lineupSection =
    lineups && (lineups.home?.length || lineups.away?.length)
      ? `<h2>التشكيلة الأساسية</h2>
         <div class="article-lineups-grid">
           <div><h3>${escapeHtml(hAr)}</h3>${lineupList(lineups.home)}</div>
           <div><h3>${escapeHtml(aAr)}</h3>${lineupList(lineups.away)}</div>
         </div>`
      : '';

  const statusLabel = status === 'Live' ? `مباشر — الدقيقة ${match.minute}` : 'نهاية المباراة';
  const title = status === 'Live'
    ? `${hAr} ${score} ${aAr}: تحديثات مباشرة وأبرز الأحداث`
    : `${hAr} ${score} ${aAr}: تقرير المباراة – ${lAr}`;
  const description = status === 'Live'
    ? `تابع مباراة ${hAr} ضد ${aAr} لحظة بلحظة: النتيجة الحالية ${score}، الأهداف وأبرز الأحداث والإحصائيات.`
    : `${hAr} ${score} ${aAr} — تقرير كامل عن المباراة يتضمن الأهداف وأبرز الإحصائيات والتشكيلتين الأساسيتين ضمن ${lAr}.`;

  const closer = pick(seed + 2, CLOSERS)(hAr, aAr);

  const body = `
    <p class="article-status-badge">${escapeHtml(statusLabel)} · ${escapeHtml(lAr)}</p>
    <p>${opener}</p>
    <h2>أبرز اللحظات</h2>
    ${eventsTimeline(events)}
    ${statsTable}
    ${lineupSection}
    <h2>${status === 'Live' ? 'ماذا بعد؟' : 'ملخص المباراة'}</h2>
    <p>${closer}</p>
    <h2>أسئلة شائعة</h2>
    <p><strong>ما هي النتيجة النهائية بين ${escapeHtml(hAr)} و${escapeHtml(aAr)}؟</strong><br>${status === 'FT' ? `انتهت المباراة بنتيجة ${escapeHtml(score)}.` : `المباراة ما زالت جارية والنتيجة الحالية هي ${escapeHtml(score)}.`}</p>
    <p><strong>من سجل أهداف اللقاء؟</strong><br>${events && events.length ? `جاءت الأهداف بتوقيع ${events.map((e) => e.playerAr || e.player).join('، ')}.` : 'تفاصيل الأهداف الكاملة مذكورة في قسم أبرز اللحظات أعلاه.'}</p>
  `;

  return { title, description, body, type: status === 'Live' ? 'live' : 'report' };
}
