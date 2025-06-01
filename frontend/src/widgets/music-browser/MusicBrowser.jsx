import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CircularProgress,
  Button,
  IconButton,
  Alert,
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { musicApi } from '../../shared/api';
import { SongCard, TagChip } from '../../shared/ui/molecules';
import { t } from '../../shared/lib/translations';

export const MusicBrowser = ({
  searchMode = false,
  searchQuery = '',
  searchResults = [],
  searchLoading = false,
  onSongPlay,
  onSongClick,
  onSongLike,
  onTagPlay,
  onDailyMixClick,
  isLiked = () => false,
  error,
  onErrorClose,
  dailyMixData = {},
  favouritesPlaylist = null,
}) => {
  const [tags, setTags] = useState([]);
  const [songs, setSongs] = useState([]);
  const [visibleTags, setVisibleTags] = useState(8);
  const [visibleSongs, setVisibleSongs] = useState(16);
  const [tagsLoading, setTagsLoading] = useState(true);
  const [songsLoading, setSongsLoading] = useState(true);
  const [loadingSongs, setLoadingSongs] = useState(false);


  useEffect(() => {
    const fetchTags = async () => {
      try {
        setTagsLoading(true);
        const response = await musicApi.getTags();
        setTags(response.data);
      } catch (err) {
        console.error('Failed to fetch tags:', err);
        onErrorClose?.(t('failedToLoadSongs'));
      } finally {
        setTagsLoading(false);
      }
    };

    fetchTags();
  }, []);


  useEffect(() => {
    const fetchInitialSongs = async () => {
      try {
        setSongsLoading(true);
        const response = await musicApi.getRandomSongs(16);
        setSongs(response.data);
      } catch (err) {
        console.error('Failed to fetch songs:', err);
        onErrorClose?.(t('failedToLoadSongs'));
      } finally {
        setSongsLoading(false);
      }
    };

    fetchInitialSongs();
  }, []);

  const handleLoadMoreTags = () => {
    setVisibleTags(prev => prev + 8);
  };

  const handleLoadMoreSongs = async () => {
    try {
      setLoadingSongs(true);
      const response = await musicApi.getRandomSongs(8);
      setSongs(prev => [...prev, ...response.data]);
      setVisibleSongs(prev => prev + 8);
    } catch (err) {
      console.error('Failed to load more songs:', err);
      onErrorClose?.(t('failedToLoadSongs'));
    } finally {
      setLoadingSongs(false);
    }
  };


  const recommendedPlaylist = {
    id: 'recommended-daily',
    title: t('dailyMix'),
    description: t('personalizedPlaylist'),
    cover: 'https://picsum.photos/seed/daily/400/400',
    color: `hsl(${Math.random() * 360}, 70%, 50%)`
  };

  const {
    currentTrack: dailyMixCurrentTrack,
    done: dailyMixDone,
    error: dailyMixError,
    loading: dailyMixLoading,
    tracksPlayed,
  } = dailyMixData;

  if (searchMode) {
    return (
      <Box sx={{ pt: 8, pb: 8, width: '100%', overflow: 'auto', flex: 1 }}>
        {error && (
          <Alert
            severity="error"
            sx={{ mb: 2, mx: 2 }}
            onClose={onErrorClose}
          >
            {error}
          </Alert>
        )}

        <Box sx={{ px: 2, mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h5">
            {t('searchResults')} "{searchQuery}"
          </Typography>
          {searchLoading && <CircularProgress size={20} />}
        </Box>

        {searchLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : searchResults.length > 0 ? (
          <Box sx={{ px: 2 }}>
            <Grid container spacing={2}>
              {searchResults.map((song) => (
                <Grid item xs={12} sm={6} md={3} key={song.id}>
                  <SongCard
                    song={song}
                    onPlay={onSongPlay}
                    onSongClick={onSongClick}
                    onLike={onSongLike}
                    isLiked={isLiked(song.id)}
                  />
                </Grid>
              ))}
            </Grid>
          </Box>
        ) : (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body1" color="text.secondary">
              {t('noSearchResults')}
            </Typography>
          </Box>
        )}
      </Box>
    );
  }

  return (
    <Box sx={{ pt: 8, pb: 8, width: '100%', overflow: 'auto', flex: 1 }}>
      {error && (
        <Alert
          severity="error"
          sx={{ mb: 2, mx: 2 }}
          onClose={onErrorClose}
        >
          {error}
        </Alert>
      )}

      {/* Tags Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" sx={{ mb: 3, px: 2 }}>
          {t('musicalTags')}
        </Typography>
        {tagsLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Box sx={{ px: 2 }}>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
              {tags.slice(0, visibleTags).map((tag, index) => (
                <TagChip
                  key={tag.id || index}
                  tag={tag}
                  onTagPlay={onTagPlay}
                />
              ))}
            </Box>
            {visibleTags < tags.length && (
              <Button 
                variant="outlined" 
                onClick={handleLoadMoreTags}
                sx={{ mt: 2 }}
              >
                {t('loadMoreTags')}
              </Button>
            )}
          </Box>
        )}
      </Box>

      {/* Recommended Playlist Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" sx={{ mb: 3, px: 2 }}>
          {t('recommendedForYou')}
        </Typography>
        <Box sx={{ px: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={8} md={6} lg={4}>
              <Card 
                onClick={onDailyMixClick}
                sx={{ 
                  cursor: 'pointer',
                  background: recommendedPlaylist.color,
                  minHeight: 120,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'scale(1.02)'
                  }
                }}
              >
                <Box sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h6" sx={{ color: 'white', fontWeight: 'bold', mb: 1 }}>
                    {recommendedPlaylist.title}
                  </Typography>
                  {dailyMixCurrentTrack ? (
                    <Typography variant="body2" sx={{ color: 'white', opacity: 0.9 }}>
                      Зараз: "{dailyMixCurrentTrack.name}" - {dailyMixCurrentTrack.artist}
                    </Typography>
                  ) : dailyMixDone ? (
                    <Typography variant="body2" sx={{ color: 'white', opacity: 0.9 }}>
                      Добірка завершена • {tracksPlayed} прослухано
                    </Typography>
                  ) : dailyMixError ? (
                    <Typography variant="body2" sx={{ color: 'white', opacity: 0.9 }}>
                      Помилка завантаження
                    </Typography>
                  ) : favouritesPlaylist?.songs?.length ? (
                    <Typography variant="body2" sx={{ color: 'white', opacity: 0.9 }}>
                      {favouritesPlaylist.songs.length} джерел для рекомендацій
                    </Typography>
                  ) : (
                    <Typography variant="body2" sx={{ color: 'white', opacity: 0.8 }}>
                      {t('personalizedPlaylist')}
                    </Typography>
                  )}
                  <Typography variant="caption" sx={{ color: 'white', opacity: 0.7, display: 'block', mt: 0.5 }}>
                    {dailyMixLoading ? '⏳ Завантаження...' : 
                     dailyMixCurrentTrack ? '🎵 Активна' :
                     dailyMixDone ? '✅ Завершено' : 
                     '🤖 ШІ рекомендації'}
                  </Typography>
                </Box>
              </Card>
            </Grid>
          </Grid>
        </Box>
      </Box>

      {/* Songs Section */}
      <Box>
        <Typography variant="h5" sx={{ mb: 3, px: 2 }}>
          {t('allMusic')}
        </Typography>
        {songsLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : songs.length > 0 ? (
          <Box sx={{ px: 2 }}>
            <Grid container spacing={2}>
              {songs.slice(0, visibleSongs).map((song) => (
                <Grid item xs={12} sm={6} md={3} key={song.id}>
                  <SongCard
                    song={song}
                    onPlay={onSongPlay}
                    onSongClick={onSongClick}
                    onLike={onSongLike}
                    isLiked={isLiked(song.id)}
                  />
                </Grid>
              ))}
            </Grid>
            {visibleSongs < songs.length && (
              <Box sx={{ textAlign: 'center', mt: 3 }}>
                <Button 
                  variant="outlined" 
                  onClick={handleLoadMoreSongs}
                  disabled={loadingSongs}
                >
                  {loadingSongs ? <CircularProgress size={20} /> : t('loadMore')}
                </Button>
              </Box>
            )}
          </Box>
        ) : (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body1" color="text.secondary">
              {t('noSongsFound')}
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
}; 