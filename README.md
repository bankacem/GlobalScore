# GlobalScore ⚽️

GlobalScore is a highly optimized, responsive, and mobile-first live football scores web application. Designed for speed, accessibility, and high SEO performance, it features standard multilingual architecture (English & Arabic) and a modular data-layer foundation. Ready for immediate deployment to GitHub Pages.

---

## 🚀 Phase 1 Features Implemented (Production Ready Foundation)

- **Multilingual Architecture (en / ar):**
  - High SEO compatibility with hreflang alternate links and canonical targets.
  - Directional attributes (`dir="rtl"` / `dir="ltr"`) handled beautifully.
  - Quick, interactive toggle button to switch language contexts.
- **PWA Capabilities:**
  - Modern `manifest.json` referencing high-quality vector brand assets (`logo.svg`).
  - Active Service Worker (`sw.js`) supporting aggressive caching of core stylesheet, javascript modules, and offline storage.
- **Mobile-First & Responsive Layouts:**
  - Standard CSS custom properties supporting a fully accessible Dark Mode toggle.
  - Critical CSS inline injection for exceptionally fast First Contentful Paint (FCP).
- **Modular Data & Layout Layer:**
  - Dynamic scores retrieved from an asynchronous `DataSource` API using standard mock resources (`live.json`).
  - Interactive components dynamically rendering in respective localized views.

---

## 📁 Directory Structure

```
globalscore/
│
├── index.html               # Language auto-detect redirect
├── robots.txt               # Crawler instructions
├── sitemap.xml              # Search engine sitemap
├── sitemap-index.xml        # Sitemap index
├── manifest.json            # PWA manifest
├── sw.js                    # Service worker caching
│
├── /en/
│   └── index.html           # English language home
│
├── /ar/
│   └── index.html           # Arabic RTL language home
│
├── /assets/
│   ├── css/
│   │   ├── critical.css     # Inlined above fold styling
│   │   └── main.css         # Responsive styling + Dark Mode definitions
│   ├── js/
│   │   ├── app.js           # Core JS entry point
│   │   ├── router.js        # Dynamic SPA Router setup
│   │   ├── data-source.js   # Dynamic fetch modular data provider
│   │   ├── components.js    # Standard rendering components
│   │   └── utils.js         # Theme & localized utilities
│   ├── img/
│   │   └── logo.svg         # Modern vector brand logo
│   └── data/
│       └── live.json        # Live mock fixtures database
│
└── README.md                # General Information and Developer Guidelines
```

---

## 🛠 Developer & Launch Instructions

### Prerequisites
You need a basic HTTP static server to run the app because it imports JavaScript files as modules (`type="module"`), which is blocked by CORS policy on the `file://` protocol.

### Run Locally
To run locally, execute either of the following commands in the project root:

Using Node's `npx`:
```bash
npx serve .
```

Or using Python's built-in server:
```bash
python3 -m http.server 8000
```

Open `http://localhost:8000/` in your browser.

---

## 🔮 Future Roadmap (Phase 2 & Beyond)
- Expand routes to support dedicated views for `/live`, `/today`, and `/leagues`.
- Match Detail, League Tables, and Standings with interactive charts.
- Dark/Light Theme persists in local storage.
- Push Notifications for match goals and updates.
- Real-time API integration.
