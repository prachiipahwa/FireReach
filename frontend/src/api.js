import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const runFireReachAgent = async (icp, companyName, targetEmail) => {
  try {
    const response = await api.post('/outreach', {
      icp,
      company_name: companyName,
      target_email: targetEmail,
    });
    return response.data;
  } catch (error) {
    console.error("Error running FireReach Agent:", error);
    throw error.response?.data || error.message;
  }
};
