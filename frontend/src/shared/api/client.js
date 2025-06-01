import axios from 'axios';
import { API_CONFIG, ENDPOINTS } from '../../config/api.js';


const api = axios.create({
    baseURL: API_CONFIG.baseURL,
    timeout: API_CONFIG.timeout,
});


api.interceptors.request.use(async (config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});


api.interceptors.response.use(
    response => response,
    error => {
        
        if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
            console.error('Backend server is not running. Please start the Flask backend on port 5000.');
            return Promise.reject({
                response: {
                    data: { message: 'Unable to connect to server. Please ensure the backend is running.' },
                    status: 503
                }
            });
        }
        

        if (error.response?.status === 401 && error.config?.url?.includes('/verify')) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            
            if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

export { api }; 