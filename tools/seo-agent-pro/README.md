# seo_agent_pro — GlobalScore Article Generator

يولّد هذا السكريبت مقالات احترافية ومحسّنة لمحركات البحث (SEO) لكل مباراة
موجودة في `assets/data/live.json`، باللغتين **العربية** و**الإنجليزية**، بدلاً
من المقالات الضعيفة/العامة السابقة.

## ما الذي يولّده لكل مباراة؟

حسب حالة المباراة (`status`) يتم اختيار نوع المقال تلقائيًا:

| الحالة (status) | نوع المقال | المحتوى |
|---|---|---|
| `Scheduled` | معاينة قبل المباراة (Preview) | موعد الانطلاق، التشكيل المتوقع، أسئلة شائعة |
| `Live` | تغطية مباشرة (Live) | النتيجة الحالية، أبرز اللحظات، الإحصائيات لحظيًا |
| `FT` | تقرير كامل (Match Report) | ملخص النتيجة، الأهداف، الإحصائيات، التشكيلتين |

كل مقال يتضمن:

- **عنوان ووصف meta فريدين** لكل مباراة (غير مكرَّرين).
- **محتوى نصي حقيقي مبني على بيانات المباراة** (الأهداف، الدقائق،
  الاستحواذ، التسديدات...) وليس نصًا عامًا (Lorem-ipsum-style).
- **بنوك جمل متعددة** (openers/closers) يتم اختيار واحدة منها بشكل ثابت
  (deterministic) حسب رقم المباراة، لتفادي تكرار نفس الجملة الافتتاحية في كل
  المقالات.
- **قسم "أسئلة شائعة" (FAQ)** يساعد على الظهور في نتائج البحث الغنية
  (Featured Snippets).
- **بيانات JSON-LD** كاملة: `SportsEvent` + `BreadcrumbList` +
  `Article`/`NewsArticle`.
- **canonical + hreflang** بين النسختين العربية والإنجليزية لنفس المباراة.
- **Open Graph / Twitter Card** meta tags.
- تصميم متطابق مع هوية الموقع (يعيد استخدام متغيرات CSS من `main.css`).

## طريقة التشغيل

```bash
node tools/seo-agent-pro/generate-articles.mjs
```

لا يحتاج السكريبت أي مكتبات خارجية (Node.js فقط، بدون `npm install`).

### ماذا يُنشئ السكريبت؟

```
en/articles/<slug>.html      مقال بالإنجليزية لكل مباراة
ar/articles/<slug>.html      نفس المقال بالعربية
en/articles/index.html       فهرس كل المقالات (EN)
ar/articles/index.html       فهرس كل المقالات (AR)
assets/css/articles.css      تنسيق المقالات (يُنسخ تلقائيًا)
sitemap.xml                  تتم إضافة روابط المقالات الجديدة تلقائيًا
```

الـ `slug` يُبنى من اسمي الفريقين ورقم المباراة، مثال:
`arsenal-vs-chelsea-1.html`.

السكريبت **آمن للتشغيل المتكرر** (idempotent): إعادة تشغيله على نفس
البيانات تعطي نفس المخرجات تمامًا (لا تظهر فروقات عشوائية في git diff)، لأن
اختيار الجمل يعتمد على seed ثابت مبني على معرّف المباراة، وليس عشوائيًا حقيقيًا.

## كيف يتم دمجه مع الموقع؟

تمت إضافة رابط "Articles / المقالات" في شريط التنقل بكل من `en/index.html`
و `ar/index.html` يوجّه إلى `articles/`.

## أتمتة التوليد (اختياري، موصى به)

لأتمتة توليد المقالات في كل مرة تتحدّث فيها `live.json` (أو حسب جدول زمني)،
يمكن إضافة GitHub Action بسيط:

```yaml
# .github/workflows/generate-articles.yml
name: Generate SEO Articles
on:
  push:
    paths:
      - "assets/data/live.json"
  schedule:
    - cron: "0 */6 * * *"   # كل 6 ساعات
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: node tools/seo-agent-pro/generate-articles.mjs
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore: regenerate SEO articles [seo_agent_pro]"
```

## التخصيص

- **بنوك الجمل**: `lib/content-en.mjs` و `lib/content-ar.mjs` — أضف المزيد من
  الجمل داخل المصفوفات (`OPENERS_WIN`, `CLOSERS`...) لزيادة التنوّع أكثر.
- **قالب الصفحة (Header/Footer/CSS)**: `lib/layout.mjs`.
- **بيانات Schema.org**: `lib/seo.mjs` → `buildJsonLd()`.
- **مصدر البيانات**: حاليًا `assets/data/live.json`. عند ربط API حقيقي لاحقًا
  (بدل البيانات الوهمية `DataSource`)، يكفي أن يستمر ملف JSON بنفس الشكل
  (`matches[]` بنفس الحقول)، والسكريبت سيعمل دون تعديل.

## قيود حالية (لأمانة الوصف)

- أسماء التشكيلة (`lineups.home/away`) لا تحتوي حاليًا على نسخة عربية في
  `live.json` (فقط أسماء هدّافي الأحداث `events[].playerAr` بها ترجمة)، لذلك
  تظهر أسماء اللاعبين في قسم "التشكيلة الأساسية" بالإنجليزية حتى داخل
  المقال العربي. لحل هذا: أضف حقلي `homeAr`/`awayAr` داخل `lineups` في
  `live.json` وسيلتقطهما القالب تلقائيًا بعد تعديل بسيط في `lib/content-ar.mjs`.
- المقالات تُبنى بمنطق قوالب (templates) ذكية مبنية على بيانات المباراة
  الفعلية، وليست عبر استدعاء نموذج ذكاء اصطناعي خارجي في وقت التشغيل — وهذا
  مقصود: يجعل التوليد فوريًا، مجانيًا، وقابلاً للتشغيل داخل GitHub Actions
  بدون مفتاح API. إن رغبت لاحقًا في مقالات أطول توليدًا بالذكاء الاصطناعي، يمكن
  استبدال دوال `buildEnglishArticle` / `buildArabicArticle` باستدعاء لأي API
  نموذج لغوي مع تمرير بيانات المباراة كسياق.
