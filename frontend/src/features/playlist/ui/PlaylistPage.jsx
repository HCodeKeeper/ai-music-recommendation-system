import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  Chip
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import ShuffleIcon from '@mui/icons-material/Shuffle';
import FavoriteIcon from '@mui/icons-material/Favorite';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { apiClient } from '../../../shared/api';
import { t } from '../../../shared/lib/translations';

const PlaylistPage = ({ 
  currentSong, 
  isPlaying, 
  onPlayPause, 
  onSongClick,
  loading: globalLoading,
  onBack,
  playlistId = 'favourites',
  onSetQueue,
  likedSongs = new Set(),
  onLike
}) => {
  const [playlist, setPlaylist] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);


  const formatDuration = (seconds) => {
    if (!seconds || isNaN(seconds)) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };


  const formatDate = (dateString) => {
    if (!dateString) return '--';
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return t('today');
    if (diffDays === 2) return t('yesterday');
    if (diffDays <= 7) return t('daysAgo', { count: diffDays });
    

    return date.toLocaleDateString('uk-UA', { 
      month: 'short', 
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
  };

  useEffect(() => {
    const fetchPlaylist = async () => {
      try {
        setLoading(true);
        let response;
        
        if (playlistId === 'favourites') {
          response = await apiClient.preferences.getFavouritesPlaylist();
        } else {

          throw new Error(t('playlistNotFound'));
        }
        
        setPlaylist(response.data);
      } catch (err) {
        console.error('Failed to fetch playlist:', err);
        setError(t('failedToLoadPlaylist'));
      } finally {
        setLoading(false);
      }
    };

    fetchPlaylist();
  }, [playlistId]);

  const handlePlayPlaylist = async () => {
    if (!playlist || !playlist.songs || playlist.songs.length === 0) return;
    
    try {

      if (onSetQueue) {
        onSetQueue(playlist.songs);
      }
      

      if (isPlaying && currentSong && playlist.songs?.some(song => song.id === currentSong.id)) {
        await onPlayPause(currentSong);
      } else {

        const firstSong = playlist.songs[0];
        await onPlayPause(firstSong);
      }
    } catch (err) {
      console.error('Failed to play/pause playlist:', err);
    }
  };

  const handleShuffle = async () => {
    if (!playlist || !playlist.songs || playlist.songs.length === 0) return;
    
    try {

      if (onSetQueue) {
        onSetQueue(playlist.songs);
      }
      

      const randomIndex = Math.floor(Math.random() * playlist.songs.length);
      const randomSong = playlist.songs[randomIndex];
      await onPlayPause(randomSong);
    } catch (err) {
      console.error('Failed to shuffle playlist:', err);
    }
  };

  const handleSongPlay = async (song) => {

    if (onSetQueue) {
      onSetQueue(playlist.songs);
    }
    
    await onPlayPause(song);
  };

  if (loading) {
    return (
      <Box sx={{ 
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !playlist) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error || t('playlistNotFound')}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column', pb: 8 }}>
      {/* Header with gradient background */}
      <Box 
        sx={{ 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          p: 4,
          pb: 2,
          minHeight: '340px',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {/* Back button */}
        <Box sx={{ mb: 2 }}>
          <IconButton 
            onClick={onBack}
            sx={{ 
              color: 'white',
              bgcolor: 'rgba(0,0,0,0.3)',
              width: 32,
              height: 32,
              '&:hover': {
                bgcolor: 'rgba(0,0,0,0.5)',
                transform: 'scale(1.04)'
              }
            }}
          >
            <ArrowBackIcon />
          </IconButton>
        </Box>

        {/* Playlist header content */}
        <Box sx={{ display: 'flex', alignItems: 'flex-end', gap: 3, width: '100%', flex: 1 }}>
          {/* Playlist Cover */}
          <Box 
            sx={{ 
              width: 232,
              height: 232,
              background: playlist.color || 'linear-gradient(135deg, #ff6b6b, #ee5a24)',
              borderRadius: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 60px rgba(0,0,0,.5)',
              flexShrink: 0
            }}
          >
            <FavoriteIcon sx={{ fontSize: 80, color: 'white', opacity: 0.9 }} />
          </Box>

          {/* Playlist Info */}
          <Box sx={{ flex: 1, pb: 2 }}>
            <Typography variant="caption" sx={{ fontWeight: 600, textTransform: 'uppercase' }}>
              Плейлисти
            </Typography>
            <Typography 
              variant="h1" 
              sx={{ 
                fontSize: { xs: '2rem', sm: '3rem', md: '4rem', lg: '5rem' },
                fontWeight: 900,
                lineHeight: 1,
                my: 2,
                wordBreak: 'break-word'
              }}
            >
              {playlist.title}
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
              {playlist.description}
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                Ваша бібліотека
              </Typography>
              <Typography variant="body2">•</Typography>
              <Typography variant="body2">
                {playlist.song_count} пісень
              </Typography>
            </Box>
          </Box>
        </Box>
      </Box>

      {/* Controls */}
      <Box 
        sx={{ 
          background: 'linear-gradient(rgba(0,0,0,.6) 0, rgba(0,0,0,.2) 100%), linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          px: 4,
          py: 3,
          display: 'flex',
          alignItems: 'center',
          gap: 2
        }}
      >
        <IconButton 
          onClick={handlePlayPlaylist}
          disabled={!playlist.songs || playlist.songs.length === 0 || globalLoading}
          sx={{ 
            bgcolor: '#1db954',
            color: 'white',
            width: 56,
            height: 56,
            '&:hover': {
              bgcolor: '#1ed760',
              transform: 'scale(1.04)'
            },
            '&:disabled': {
              bgcolor: 'rgba(255,255,255,0.3)'
            }
          }}
        >
          {globalLoading && currentSong && playlist.songs?.some(song => song.id === currentSong.id) ? (
            <CircularProgress size={24} color="inherit" />
          ) : isPlaying && currentSong && playlist.songs?.some(song => song.id === currentSong.id) ? (
            <PauseIcon sx={{ fontSize: 28 }} />
          ) : (
            <PlayArrowIcon sx={{ fontSize: 28 }} />
          )}
        </IconButton>

        <IconButton 
          onClick={handleShuffle}
          disabled={!playlist.songs || playlist.songs.length === 0}
          sx={{ 
            color: 'white',
            width: 32,
            height: 32,
            '&:hover': {
              bgcolor: 'rgba(255,255,255,0.1)'
            }
          }}
        >
          <ShuffleIcon />
        </IconButton>
      </Box>

      {/* Track List */}
      <Box sx={{ flex: 1, overflow: 'auto', bgcolor: 'background.default' }}>
        {playlist.songs && playlist.songs.length > 0 ? (
          <TableContainer>
            <Table sx={{ minWidth: 650 }}>
              <TableHead>
                <TableRow sx={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                  <TableCell sx={{ color: 'text.secondary', fontWeight: 500, width: 50, pl: 3 }}>
                    #
                  </TableCell>
                  <TableCell sx={{ color: 'text.secondary', fontWeight: 500 }}>
                    Назва
                  </TableCell>
                  <TableCell sx={{ color: 'text.secondary', fontWeight: 500 }}>
                    Альбом
                  </TableCell>
                  <TableCell sx={{ color: 'text.secondary', fontWeight: 500 }}>
                    Дата додавання
                  </TableCell>
                  <TableCell sx={{ color: 'text.secondary', fontWeight: 500, width: 60, textAlign: 'center' }}>
                    <FavoriteIcon sx={{ fontSize: 18 }} />
                  </TableCell>
                  <TableCell sx={{ color: 'text.secondary', fontWeight: 500, width: 80, textAlign: 'center' }}>
                    <AccessTimeIcon sx={{ fontSize: 18 }} />
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {playlist.songs.map((song, index) => (
                  <TableRow 
                    key={song.id}
                    sx={{ 
                      cursor: 'pointer',
                      '&:hover': {
                        bgcolor: 'rgba(255,255,255,0.05)',
                        '& .song-number': {
                          opacity: 0
                        },
                        '& .hover-play-button': {
                          opacity: 1
                        }
                      },
                      bgcolor: currentSong?.id === song.id ? 'rgba(255,255,255,0.08)' : 'transparent'
                    }}
                  >
                    <TableCell sx={{ pl: 3, color: currentSong?.id === song.id ? '#1db954' : 'text.secondary', position: 'relative' }}>
                      {currentSong?.id === song.id ? (

                        isPlaying ? (
                          <IconButton 
                            onClick={(e) => {
                              e.stopPropagation();
                              handleSongPlay(song);
                            }}
                            disabled={globalLoading}
                            sx={{ 
                              width: 20,
                              height: 20,
                              minWidth: 20,
                              padding: 0,
                              color: '#1db954',
                              '&:hover': {
                                color: '#1ed760',
                                bgcolor: 'transparent'
                              }
                            }}
                          >
                            {globalLoading ? (
                              <CircularProgress size={16} color="inherit" />
                            ) : (
                              <PauseIcon sx={{ fontSize: 16 }} />
                            )}
                          </IconButton>
                        ) : (
                          <IconButton 
                            onClick={(e) => {
                              e.stopPropagation();
                              handleSongPlay(song);
                            }}
                            disabled={globalLoading}
                            sx={{ 
                              width: 20,
                              height: 20,
                              minWidth: 20,
                              padding: 0,
                              color: '#1db954',
                              '&:hover': {
                                color: '#1ed760',
                                bgcolor: 'transparent'
                              }
                            }}
                          >
                            {globalLoading ? (
                              <CircularProgress size={16} color="inherit" />
                            ) : (
                              <PlayArrowIcon sx={{ fontSize: 16 }} />
                            )}
                          </IconButton>
                        )
                      ) : (

                        <>
                          <Box 
                            className="song-number"
                            sx={{ 
                              position: 'absolute',
                              top: '50%',
                              left: '50%',
                              transform: 'translate(-50%, -50%)',
                              transition: 'opacity 0.2s',
                              opacity: 1
                            }}
                          >
                            {index + 1}
                          </Box>
                          <IconButton 
                            className="hover-play-button"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleSongPlay(song);
                            }}
                            disabled={globalLoading}
                            sx={{ 
                              position: 'absolute',
                              top: '50%',
                              left: '50%',
                              transform: 'translate(-50%, -50%)',
                              width: 20,
                              height: 20,
                              minWidth: 20,
                              padding: 0,
                              opacity: 0,
                              transition: 'opacity 0.2s',
                              color: 'text.primary',
                              '&:hover': {
                                color: '#1db954',
                                bgcolor: 'transparent'
                              }
                            }}
                          >
                            <PlayArrowIcon sx={{ fontSize: 16 }} />
                          </IconButton>
                        </>
                      )}
                    </TableCell>
                    <TableCell onClick={() => onSongClick(song)}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box>
                          <Typography 
                            variant="body2" 
                            sx={{ 
                              fontWeight: 500,
                              color: currentSong?.id === song.id ? '#1db954' : 'text.primary'
                            }}
                          >
                            {song.name}
                            {song.pathToTrack && (
                              <Box
                                component="span"
                                sx={{
                                  width: 6,
                                  height: 6,
                                  borderRadius: '50%',
                                  backgroundColor: 'success.main',
                                  display: 'inline-block',
                                  ml: 1,
                                  verticalAlign: 'middle'
                                }}
                              />
                            )}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {song.artist}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell onClick={() => onSongClick(song)}>
                      <Typography variant="body2" color="text.secondary">
                        {song.genre || '--'}
                      </Typography>
                    </TableCell>
                    <TableCell onClick={() => onSongClick(song)}>
                      <Typography variant="body2" color="text.secondary">
                        {formatDate(song.added_to_favourites)}
                      </Typography>
                    </TableCell>
                    <TableCell sx={{ textAlign: 'center' }}>
                      <IconButton 
                        onClick={(e) => {
                          e.stopPropagation();
                          onLike && onLike(song.id, likedSongs.has(song.id));
                        }}
                        sx={{ 
                          color: likedSongs.has(song.id) ? 'success.main' : 'text.secondary',
                          '&:hover': {
                            color: likedSongs.has(song.id) ? 'success.light' : 'success.main'
                          }
                        }}
                      >
                        <FavoriteIcon sx={{ fontSize: 18 }} />
                      </IconButton>
                    </TableCell>
                    <TableCell sx={{ textAlign: 'center' }} onClick={() => onSongClick(song)}>
                      <Typography variant="body2" color="text.secondary">
                        {formatDuration(song.duration)}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column',
            alignItems: 'center', 
            justifyContent: 'center', 
            height: 200,
            textAlign: 'center',
            p: 3
          }}>
            <FavoriteIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Поки що немає улюблених пісень
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Пісні, які вам подобаються, з'являться тут
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default PlaylistPage; 