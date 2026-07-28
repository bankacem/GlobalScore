export class Router {
  constructor(routes) {
    this.routes = routes;
    window.addEventListener('hashchange', () => this.handleRoute());
    window.addEventListener('load', () => this.handleRoute());
  }

  handleRoute() {
    const rawHash = window.location.hash || '#today';
    // If hash has parameters like #match-1
    const cleanHash = rawHash.split('-')[0];
    const param = rawHash.split('-')[1] || null;

    const route = this.routes[cleanHash] || this.routes['#today'];
    if (route) {
      route(param);
    }
  }

  static navigate(hash) {
    window.location.hash = hash;
  }
}
