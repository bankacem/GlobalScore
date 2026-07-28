export class DataSource {
  async getLiveMatches() {
    try {
      const res = await fetch('/assets/data/live.json');
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      return await res.json();
    } catch (e) {
      console.error("Error fetching live matches: ", e);
      return [];
    }
  }
}
