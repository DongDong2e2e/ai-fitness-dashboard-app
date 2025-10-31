import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api', // 백엔드 API 주소
  headers: {
    'Content-Type': 'application/json',
  },
});

export const addWorkoutLog = (logData) => {
  return apiClient.post('/workout-logs', logData);
};

export const addInbodyRecord = (inbodyData) => {
  return apiClient.post('/inbody-records', inbodyData);
};

export const getDashboardData = () => {
    return apiClient.get('/dashboard-data');
};
