import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  IconButton,
  InputBase,
  alpha,
  CircularProgress,
  Alert,
  Chip,
  LinearProgress
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import AlbumIcon from '@mui/icons-material/Album';
import { apiClient } from '../../../shared/api';
import { t } from '../../../shared/lib/translations';

function ColdStartPage({ onComplete }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [initialSongs, setInitialSongs] = useState([]);
  const [selectedSongs, setSelectedSongs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [preferencesLoading, setPreferencesLoading] = useState(true);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const REQUIRED_SONGS = 5;


  useEffect(() => {
    const fetchExistingPreferences = async () => {
      try {
        setPreferencesLoading(true);
        const response = await apiClient.preferences.getPreferences();
        
        if (response.data && response.data.length > 0) {

          const existingPreferredSongs = response.data
            .filter(pref => pref.song) 
            .map(pref => pref.song);
          
          setSelectedSongs(existingPreferredSongs);
          console.log(`Found ${existingPreferredSongs.length} existing preferences:`, existingPreferredSongs.map(s => s.name));
        }
      } catch (err) {
        console.error('Failed to fetch existing preferences:', err);

      } finally {
        setPreferencesLoading(false);
      }
    };

    fetchExistingPreferences();
  }, []);


  useEffect(() => {
    const fetchInitialSongs = async () => {
      try {
        setInitialLoading(true);
        const response = await apiClient.music.getRandomSongs(20, [], true);
        setInitialSongs(response.data);
      } catch (err) {
        console.error('Failed to fetch initial songs:', err);
        setError(t('failedToLoad'));
      } finally {
        setInitialLoading(false);
      }
    };

    fetchInitialSongs();
  }, []);


  useEffect(() => {
    const searchSongs = async (query) => {
      if (!query.trim()) {
        setSearchResults([]);
        return;
      }

      try {
        setSearchLoading(true);
        const response = await apiClient.music.searchSongs(query.trim(), 20);
        setSearchResults(response.data);
      } catch (err) {
        console.error('Search failed:', err);
        setError(t('searchFailed'));
        setSearchResults([]);
      } finally {
        setSearchLoading(false);
      }
    };


    const timeoutId = setTimeout(() => {
      if (searchQuery) {
        searchSongs(searchQuery);
      } else {
        setSearchResults([]);
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  const handleAddSong = (song) => {
    if (selectedSongs.length >= REQUIRED_SONGS) {
      setError(t('maxSongsSelected', { count: REQUIRED_SONGS }));
      return;
    }

    if (selectedSongs.find(s => s.id === song.id)) {
      setError(t('songAlreadySelected'));
      return;
    }

    setSelectedSongs(prev => [...prev, song]);
    setError('');
  };

  const handleRemoveSong = (songId) => {
    setSelectedSongs(prev => prev.filter(s => s.id !== songId));
    setError('');
  };

  const handleSubmit = async () => {
    if (selectedSongs.length !== REQUIRED_SONGS) {
      setError(t('selectExactlySongs', { count: REQUIRED_SONGS }));
      return;
    }

    try {
      setSubmitting(true);
      const songIds = selectedSongs.map(song => song.id);
      await apiClient.preferences.addPreferences(songIds);
      onComplete();
    } catch (err) {
      console.error('Failed to save preferences:', err);
      setError(t('failedToSave'));
    } finally {
      setSubmitting(false);
    }
  };

  const clearError = () => {
    setError('');
  };


  if (preferencesLoading) {
    return (
      <Box sx={{ 
        minHeight: '100vh',
        width: '100vw',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          {t('loadingPreferences')}
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      minHeight: '100vh',
      width: '100vw',
      display: 'flex',
      flexDirection: 'column',
      p: 3
    }}>
      {/* Header */}
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h3" gutterBottom>
          {selectedSongs.length > 0 ? t('updatePreferences') : t('welcomeMessage')}
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          {selectedSongs.length > 0 ? 
            t('modifySelection') : 
            t('selectFiveSongs')
          }
        </Typography>
        
        {/* Progress indicator */}
        <Box sx={{ mt: 3, mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {t('selectedSongs')}: {selectedSongs.length}/{REQUIRED_SONGS}
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={(selectedSongs.length / REQUIRED_SONGS) * 100}
            sx={{ 
              height: 8,
              borderRadius: 4,
              backgroundColor: 'rgba(255,255,255,0.1)',
              '& .MuiLinearProgress-bar': {
                borderRadius: 4
              }
            }}
          />
        </Box>
      </Box>

      {/* Error display */}
      {error && (
        <Alert 
          severity="error" 
          onClose={clearError}
          sx={{ mb: 3, maxWidth: 600, mx: 'auto' }}
        >
          {error}
        </Alert>
      )}

      {/* Selected songs */}
      {selectedSongs.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom sx={{ textAlign: 'center' }}>
            {t('selectedSongs')}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: 'center' }}>
            {selectedSongs.map((song) => (
              <Chip
                key={song.id}
                label={`${song.name} - ${song.artist}`}
                onDelete={() => handleRemoveSong(song.id)}
                color="primary"
                variant="filled"
                sx={{ maxWidth: 300 }}
              />
            ))}
          </Box>
        </Box>
      )}

      {/* Search bar */}
      <Box sx={{ maxWidth: 600, mx: 'auto', mb: 4, width: '100%' }}>
        <Box 
          sx={{ 
            position: 'relative',
            borderRadius: 1,
            bgcolor: (theme) => alpha(theme.palette.common.white, 0.15),
            '&:hover': {
              bgcolor: (theme) => alpha(theme.palette.common.white, 0.25),
            },
            border: 1,
            borderColor: 'divider'
          }}
        >
          <Box sx={{ p: '8px 12px', display: 'flex', alignItems: 'center' }}>
            <IconButton sx={{ p: '10px' }} aria-label="search">
              {searchLoading ? (
                <CircularProgress size={20} />
              ) : (
                <SearchIcon />
              )}
            </IconButton>
            <InputBase
              sx={{ ml: 1, flex: 1 }}
              placeholder={t('searchPlaceholder')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              inputProps={{ 'aria-label': 'search songs' }}
            />
          </Box>
        </Box>
      </Box>

      {/* Song results - either search results or initial random songs */}
      {(searchResults.length > 0 || (!searchQuery && initialSongs.length > 0)) && (
        <Box sx={{ flex: 1, mb: 4 }}>
          <Typography variant="h6" gutterBottom sx={{ textAlign: 'center' }}>
            {searchQuery ? t('searchResults') : t('popularSongs')}
          </Typography>
          
          {initialLoading && !searchQuery ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <Grid container spacing={2} sx={{ justifyContent: 'center' }}>
              {(searchQuery ? searchResults : initialSongs).map((song) => {
                const isSelected = selectedSongs.find(s => s.id === song.id);
                const canAdd = selectedSongs.length < REQUIRED_SONGS;
                
                return (
                  <Grid item xs={12} sm={6} md={4} lg={3} key={song.id}>
                    <Card 
                      sx={{ 
                        height: 300,
                        display: 'flex',
                        flexDirection: 'column',
                        opacity: isSelected ? 0.6 : 1,
                        border: isSelected ? 2 : 0,
                        borderColor: 'primary.main'
                      }}
                    >
                      <Box 
                        sx={{ 
                          height: 180,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          backgroundColor: 'background.paper'
                        }}
                      >
                        <AlbumIcon 
                          sx={{ 
                            fontSize: 80,
                            color: 'text.secondary',
                            opacity: 0.7
                          }} 
                        />
                      </Box>
                      <CardContent 
                        sx={{ 
                          flex: 1,
                          display: 'flex',
                          flexDirection: 'column',
                          justifyContent: 'space-between',
                          p: 2
                        }}
                      >
                        <Box>
                          <Typography 
                            variant="subtitle1" 
                            sx={{ 
                              fontWeight: 600,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                              display: 'flex',
                              alignItems: 'center',
                              gap: 0.5
                            }}
                            title={song.name}
                          >
                            {song.pathToTrack && (
                              <Box
                                sx={{
                                  width: 6,
                                  height: 6,
                                  borderRadius: '50%',
                                  backgroundColor: 'success.main',
                                  flexShrink: 0
                                }}
                              />
                            )}
                            <Box sx={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>
                              {song.name}
                            </Box>
                          </Typography>
                          <Typography 
                            variant="body2"
                            color="text.secondary"
                            sx={{ 
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap'
                            }}
                            title={song.artist}
                          >
                            {song.artist}
                          </Typography>
                          {song.genre && (
                            <Typography 
                              variant="caption"
                              sx={{ 
                                fontSize: '0.75rem',
                                color: 'primary.main',
                                fontWeight: 500,
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap',
                                maxWidth: 180,
                                display: 'block'
                              }}
                              title={`Tag: ${song.genre}`}
                            >
                              {song.genre}
                            </Typography>
                          )}
                        </Box>
                        
                        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 1 }}>
                          {isSelected ? (
                            <IconButton 
                              onClick={() => handleRemoveSong(song.id)}
                              color="error"
                              size="small"
                            >
                              <RemoveIcon />
                            </IconButton>
                          ) : (
                            <IconButton 
                              onClick={() => handleAddSong(song)}
                              color="primary"
                              size="small"
                              disabled={!canAdd}
                            >
                              <AddIcon />
                            </IconButton>
                          )}
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                );
              })}
            </Grid>
          )}
        </Box>
      )}

      {/* Submit button */}
      <Box sx={{ textAlign: 'center', mt: 4 }}>
        <Button
          variant="contained"
          size="large"
          onClick={handleSubmit}
          disabled={selectedSongs.length !== REQUIRED_SONGS || submitting}
          sx={{ minWidth: 200 }}
        >
          {submitting ? (
            <CircularProgress size={24} color="inherit" />
          ) : (
            selectedSongs.length === REQUIRED_SONGS 
              ? t('savePreferences')
              : t('continueWithSongs', { count: selectedSongs.length, total: REQUIRED_SONGS })
          )}
        </Button>
      </Box>
    </Box>
  );
}

export default ColdStartPage; 