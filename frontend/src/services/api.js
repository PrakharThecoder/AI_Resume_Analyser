import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for global error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear token if unauthorized
      localStorage.removeItem('token');
      // We'll let the components handle the redirect via AuthContext
    }
    return Promise.reject(error);
  }
);

export const dashboardService = {
  getAnalytics: async () => {
    try {
      const response = await api.get('/dashboard');
      return response.data;
    } catch (error) {
      if (error.response && error.response.status === 404) {
        return {
          ats_score: 0,
          skill_match_percentage: 0,
          matched_skills: [],
          missing_skills: [],
          resume_sections: [],
          candidate_summary: "No analysis found. Please upload a resume to get started.",
          strengths: [],
          improvement_recommendations: []
        };
      }
      console.error("Error fetching analytics:", error);
      throw error;
    }
  }
};

export const resumeService = {
  uploadResume: async (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress
    });
    return response.data;
  },
  getResumes: async () => {
    const response = await api.get('/resumes/');
    return response.data;
  },
  deleteResume: async (id) => {
    const response = await api.delete(`/resumes/${id}`);
    return response.data;
  },
  analyzeResume: async (id, role = "Software Engineer") => {
    const response = await api.post(`/resumes/${id}/analyze?role=${encodeURIComponent(role)}`);
    return response.data;
  }
};

export default api;
