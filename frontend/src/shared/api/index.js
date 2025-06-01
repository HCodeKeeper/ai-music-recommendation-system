import { authApi } from './auth.js';
import { musicApi } from './music.js';
import { preferencesApi } from './preferences.js';
import { api } from './client.js';


export { authApi, musicApi, preferencesApi, api };


export const apiClient = {
    auth: authApi,
    music: musicApi,
    preferences: preferencesApi,
    recommendations: {
        get: (trackId, options = {}) => 
            api.post(`/recommendations/${trackId}`, options),
        search: (query) => 
            api.get(`/search?q=${encodeURIComponent(query)}`)
    }
}; 