import { api } from './client.js';
import { ENDPOINTS } from '../../config/api.js';

export const musicApi = {
    getRandomSongs: (count = 20, excludeIds = []) => {
        const params = new URLSearchParams({ count: count.toString() });
        if (excludeIds.length > 0) {
            params.append('exclude', excludeIds.join(','));
        }
        return api.get(`${ENDPOINTS.music.random}?${params}`);
    },
    
    getTags: () =>
        api.get(ENDPOINTS.music.tags),
    
    getSongDetails: (songId) =>
        api.get(`${ENDPOINTS.music.songs}/${songId}`),
    
    searchSongs: (query, limit = 20) => {
        const params = new URLSearchParams({ q: query, limit: limit.toString() });
        return api.get(`${ENDPOINTS.music.search}?${params}`);
    },
    
    getRecommendations: (seedId, limit = 10) => 
        api.get(`${ENDPOINTS.music.recommendations}?seed_id=${seedId}&limit=${limit}`),
    
    getDailyMix: (excludeIds = [], seedId = null) => {
        const params = new URLSearchParams();
        if (excludeIds.length > 0) {
            params.append('exclude', excludeIds.join(','));
        }
        if (seedId) {
            params.append('seed_id', seedId);
        }
        return api.get(`${ENDPOINTS.music.dailyMix}?${params}`);
    },
    
    getSongsByGenre: (genre, limit = 20) => {
        const params = new URLSearchParams({ genre, limit: limit.toString() });
        return api.get(`${ENDPOINTS.music.byGenre}?${params}`);
    },
    
    getGenreRecommendationsFromFavorites: (genre, limit = 20) => {
        const params = new URLSearchParams({ genre, limit: limit.toString() });
        return api.get(`${ENDPOINTS.music.genreRecommendationsFromFavorites}?${params}`);
    }
}; 