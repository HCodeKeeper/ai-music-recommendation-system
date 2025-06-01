import { useState, useEffect, useCallback } from 'react';
import { musicApi } from '../../../shared/api';

export const useSearch = (debounceMs = 500) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearchMode, setIsSearchMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);


  useEffect(() => {
    const searchSongs = async (query) => {
      if (!query.trim()) {
        setSearchResults([]);
        setIsSearchMode(false);
        setError(null);
        return;
      }

      try {
        setLoading(true);
        setIsSearchMode(true);
        setError(null);
        
        const response = await musicApi.searchSongs(query.trim(), 50);
        setSearchResults(response.data);
      } catch (err) {
        console.error('Search failed:', err);
        setError('Search failed. Please try again.');
        setSearchResults([]);
      } finally {
        setLoading(false);
      }
    };


    const timeoutId = setTimeout(() => {
      if (searchQuery) {
        searchSongs(searchQuery);
      } else {
        setSearchResults([]);
        setIsSearchMode(false);
        setError(null);
      }
    }, debounceMs);

    return () => clearTimeout(timeoutId);
  }, [searchQuery, debounceMs]);


  const clearSearch = useCallback(() => {
    setSearchQuery('');
    setSearchResults([]);
    setIsSearchMode(false);
    setError(null);
  }, []);


  const handleSearchChange = useCallback((event) => {
    setSearchQuery(event.target.value);
  }, []);

  return {

    searchQuery,
    searchResults,
    isSearchMode,
    loading,
    error,
    

    setSearchQuery,
    clearSearch,
    handleSearchChange,
  };
}; 