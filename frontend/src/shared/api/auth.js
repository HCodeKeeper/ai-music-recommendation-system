import { api } from './client.js';
import { ENDPOINTS } from '../../config/api.js';

export const authApi = {
    login: (email, password) => 
        api.post(ENDPOINTS.auth.login, { email, password }),
    
    register: (email, password, name) => 
        api.post(ENDPOINTS.auth.register, { email, password, name }),
    
    verifyToken: () => 
        api.get(ENDPOINTS.auth.verify)
}; 