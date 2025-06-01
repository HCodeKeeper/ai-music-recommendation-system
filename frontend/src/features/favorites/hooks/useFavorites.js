import { useState, useEffect, useCallback } from 'react';
import { preferencesApi } from '../../../shared/api';

export const useFavorites = () => {
  const [likedSongs, setLikedSongs] = useState(new Set());
  const [favouritesPlaylist, setFavouritesPlaylist] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);


  useEffect(() => {
    const fetchLikedSongs = async () => {
      try {
        setLoading(true);
        const response = await preferencesApi.getPreferences();
        const likedSongIds = new Set(response.data.map(pref => pref.song_id));
        setLikedSongs(likedSongIds);
      } catch (err) {
        console.error('Failed to fetch liked songs:', err);
        setError('Failed to load favorites');
      } finally {
        setLoading(false);
      }
    };

    fetchLikedSongs();
  }, []);


  useEffect(() => {
    const fetchFavouritesPlaylist = async () => {
      try {
        const response = await preferencesApi.getFavouritesPlaylist();
        setFavouritesPlaylist(response.data);
      } catch (err) {
        console.error('Failed to fetch favourites playlist:', err);

      }
    };

    fetchFavouritesPlaylist();
  }, []);


  const handleLike = useCallback(async (songId, currentlyLiked) => {
    try {
      setError(null);
      
      if (currentlyLiked) {
        // Unlike the song
        await preferencesApi.removePreference(songId);
        setLikedSongs(prev => {
          const newSet = new Set(prev);
          newSet.delete(songId);
          return newSet;
        });
        
        // Update favourites playlist if it exists
        if (favouritesPlaylist) {
          setFavouritesPlaylist(prev => ({
            ...prev,
            songs: prev.songs.filter(song => song.id !== songId),
            song_count: prev.song_count - 1
          }));
        }
      } else {
        // Like the song
        await preferencesApi.addPreference(songId);
        setLikedSongs(prev => new Set(prev).add(songId));
        
        // Refetch favourites playlist to get updated list with new song
        const response = await preferencesApi.getFavouritesPlaylist();
        setFavouritesPlaylist(response.data);
      }
    } catch (err) {
      console.error('Failed to update song preference:', err);
      setError('Failed to update favorites');
    }
  }, [favouritesPlaylist]);

  // Check if a song is liked
  const isSongLiked = useCallback((songId) => {
    return likedSongs.has(songId);
  }, [likedSongs]);

  // Get liked songs count
  const getLikedSongsCount = useCallback(() => {
    return likedSongs.size;
  }, [likedSongs]);

  // Refresh favorites data
  const refreshFavorites = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch both liked songs and playlist
      const [preferencesResponse, playlistResponse] = await Promise.all([
        preferencesApi.getPreferences(),
        preferencesApi.getFavouritesPlaylist()
      ]);
      
      const likedSongIds = new Set(preferencesResponse.data.map(pref => pref.song_id));
      setLikedSongs(likedSongIds);
      setFavouritesPlaylist(playlistResponse.data);
    } catch (err) {
      console.error('Failed to refresh favorites:', err);
      setError('Failed to refresh favorites');
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    // State
    likedSongs,
    favouritesPlaylist,
    loading,
    error,
    
    // Actions
    handleLike,
    isSongLiked,
    getLikedSongsCount,
    refreshFavorites,
    
    // Utilities
    hasFavorites: likedSongs.size > 0,
    hasPlaylist: Boolean(favouritesPlaylist?.songs?.length),
  };
}; 