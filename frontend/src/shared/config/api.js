export const API_BASE_URL = 'http://localhost:5000';

export const API_ENDPOINTS = {

  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    VERIFY: '/api/auth/verify',
  },
  

  MUSIC: {
    RANDOM: '/api/music/random',
    SEARCH: '/api/music/search',
    TAGS: '/api/music/tags',
    FILE: (songId) => `/api/music/file/${songId}`,
    BY_GENRE: '/api/music/by-genre',
    DETAILS: (songId) => `/api/music/songs/${songId}`,
    DAILY_MIX: '/api/music/daily-mix',
  },
  

  PREFERENCES: {
    GET: '/api/preferences',
    ADD: '/api/preferences',
    REMOVE: (songId) => `/api/preferences/${songId}`,
    FAVOURITES: '/api/preferences/favourites-playlist',
  },
};

export const apiConfig = {
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
}; 