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
