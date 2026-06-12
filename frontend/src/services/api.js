import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const dashboardService = {
  getAnalytics: async () => {
    try {
      // Fetching from the newly created dashboard debug endpoint
      const response = await api.get('/dashboard/debug');
      return response.data;
    } catch (error) {
      console.error("Error fetching analytics:", error);
      throw error;
    }
  }
};
