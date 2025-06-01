import { api } from './client.js';
import { ENDPOINTS } from '../../config/api.js';

export const preferencesApi = {
    checkColdStart: () => 
        api.get(ENDPOINTS.preferences.checkColdStart),
    
    addPreferences: (songIds) => 
        api.post(ENDPOINTS.preferences.addPreferences, { song_ids: songIds }),
    
    getPreferences: () => 
        api.get(ENDPOINTS.preferences.getPreferences),
    
    addPreference: (songId) => 
        api.post(ENDPOINTS.preferences.addPreference, { song_id: songId }),
    
    removePreference: (songId) => 
        api.delete(ENDPOINTS.preferences.removePreference, { data: { song_id: songId } }),
    
    getFavouritesPlaylist: () =>
        api.get(ENDPOINTS.preferences.favouritesPlaylist)
}; 