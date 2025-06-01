import { useState, useCallback } from 'react';
import { musicApi } from '../../../shared/api';

export const useTagBrowser = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleTagPlay = useCallback(async (tag, onSongPlay, onQueueUpdate) => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('Playing tag:', tag);
      

      const tagToSearch = typeof tag === 'string' ? tag : tag.name;
      

      const response = await musicApi.searchSongs(tagToSearch, 20);
      const tagSongs = response.data;
      
      if (tagSongs.length === 0) {
        throw new Error('No songs found for this tag');
      }
      

      onQueueUpdate?.(tagSongs);
      

      const firstSong = tagSongs[0];
      await onSongPlay?.(firstSong);
      
      console.log(`Playing ${tagSongs.length} songs for tag: ${tagToSearch}`);
    } catch (err) {
      console.error('Failed to play tag:', err);
      setError(`Failed to play tag: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {

    loading,
    error,
    

    handleTagPlay,
    clearError,
  };
}; 