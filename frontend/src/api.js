import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const startWorkflow = async (icp) => {
  try {
    const response = await api.post('/outreach/start', { icp });
    return response.data;
  } catch (error) {
    console.error("Error starting FireReach workflow:", error);
    throw error.response?.data || error.message;
  }
};

export const resumeWorkflow = async (threadId, stateUpdate) => {
  try {
    const response = await api.post('/outreach/resume', {
      thread_id: threadId,
      ...stateUpdate
    });
    return response.data;
  } catch (error) {
    console.error("Error resuming FireReach workflow:", error);
    throw error.response?.data || error.message;
  }
};
