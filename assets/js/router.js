// Simple Router placeholder for future routing implementation in Phase 2
export class Router {
  constructor(routes) {
    this.routes = routes;
    window.addEventListener('hashchange', () => this.handleRoute());
    window.addEventListener('load', () => this.handleRoute());
  }

  handleRoute() {
    const hash = window.location.hash || '#home';
    const route = this.routes[hash] || this.routes['#home'];
    if (route) {
      route();
    }
  }
}
