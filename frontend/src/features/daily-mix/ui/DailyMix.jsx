import React, { useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  LinearProgress,
  Chip,
  Stack,
  Alert,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  SkipNext as SkipIcon,
  Favorite as FavoriteIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import useDailyMix from '../hooks/useDailyMix';

const DailyMix = ({ 
  favourites = [], 
  onPlaySong, 
  currentSong, 
  isPlaying, 
  sx = {} 
}) => {
  const {
    currentTrack,
    queue,
    currentSeed,
    loading,
    error,
    done,
    seedsRemaining,
    tracksPlayed,
    tracksSkipped,
    next,
    likeCurrent,
    skipCurrent,
    reset
  } = useDailyMix(favourites.map(f => f.id || f.song_id));


  useEffect(() => {
    if (currentTrack && onPlaySong) {
      onPlaySong(currentTrack);
    }
  }, [currentTrack, onPlaySong]);

  const formatPlaylistStats = () => {
    const total = tracksPlayed + tracksSkipped;
    if (total === 0) return 'Розпочинаємо...';
    return `${total} пісень прослухано • ${seedsRemaining} джерел залишилось`;
  };

  const isCurrentTrackPlaying = currentTrack && currentSong?.id === currentTrack.id && isPlaying;

  if (!favourites || favourites.length === 0) {
    return (
      <Card sx={{ ...sx, minHeight: 200 }}>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" gutterBottom>
            🎵 Щоденна добірка
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Додайте кілька улюблених пісень, щоб отримувати персональні рекомендації
          </Typography>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ ...sx, minHeight: 200 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            🎵 Щоденна добірка
          </Typography>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
          <Button 
            variant="outlined" 
            onClick={reset} 
            startIcon={<RefreshIcon />}
            fullWidth
          >
            Спробувати знову
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (done) {
    return (
      <Card sx={{ ...sx, minHeight: 200 }}>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" gutterBottom>
            🎵 Щоденна добірка завершена
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {formatPlaylistStats()}
          </Typography>
          <Button 
            variant="contained" 
            onClick={reset} 
            startIcon={<RefreshIcon />}
          >
            Почати знову
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!currentTrack) {
    return (
      <Card sx={{ ...sx, minHeight: 200 }}>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" gutterBottom>
            🎵 Щоденна добірка
          </Typography>
          {loading ? (
            <>
              <LinearProgress sx={{ mb: 2 }} />
              <Typography variant="body2" color="text.secondary">
                Підготовляємо рекомендації...
              </Typography>
            </>
          ) : (
            <Button 
              variant="contained" 
              onClick={next} 
              startIcon={<PlayIcon />}
              size="large"
            >
              Розпочати
            </Button>
          )}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ ...sx, minHeight: 200 }}>
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">
            🎵 Щоденна добірка
          </Typography>
          <Tooltip title="Інформація про алгоритм">
            <IconButton size="small">
              <InfoIcon />
            </IconButton>
          </Tooltip>
        </Box>

        {/* Current Seed Info */}
        {currentSeed && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="caption" color="text.secondary">
              На основі:
            </Typography>
            <Typography variant="body2" sx={{ fontWeight: 500 }}>
              "{currentSeed.name}" - {currentSeed.artist}
            </Typography>
          </Box>
        )}

        {/* Current Track */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Зараз грає:
          </Typography>
          
          <Box sx={{ mb: 2 }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 0.5 }}>
              {currentTrack.name}
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              {currentTrack.artist}
            </Typography>
            
            {/* Genre and features */}
            <Stack direction="row" spacing={1} sx={{ mt: 1, flexWrap: 'wrap', gap: 0.5 }}>
              {currentTrack.genre && (
                <Chip label={currentTrack.genre} size="small" variant="outlined" />
              )}
              {currentTrack.pathToTrack && (
                <Chip 
                  label="Доступна для відтворення" 
                  size="small" 
                  color="success" 
                  variant="outlined" 
                />
              )}
            </Stack>
          </Box>

          {/* Recommendation Explanation */}
          {currentTrack.recommendation_explanation && (
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>Чому ця пісня:</strong><br />
                Схожа на "{currentTrack.recommendation_explanation.seed_song}" від {currentTrack.recommendation_explanation.seed_artist}
                {currentTrack.recommendation_explanation.features && 
                 currentTrack.recommendation_explanation.features.length > 0 && (
                  <>
                    <br />
                    <em>Схожі характеристики: {currentTrack.recommendation_explanation.features.slice(0, 3).join(', ')}</em>
                  </>
                )}
              </Typography>
            </Alert>
          )}
        </Box>

        <Divider sx={{ mb: 2 }} />

        {/* Controls */}
        <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
          <Button
            variant="contained"
            color="success"
            startIcon={<FavoriteIcon />}
            onClick={likeCurrent}
            disabled={loading}
            size="large"
            sx={{ flex: 1 }}
          >
            Подобається
          </Button>
          
          <Button
            variant="outlined"
            startIcon={<SkipIcon />}
            onClick={skipCurrent}
            disabled={loading}
            size="large"
            sx={{ flex: 1 }}
          >
            Пропустити
          </Button>
        </Stack>

        {/* Progress/Stats */}
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            {formatPlaylistStats()}
          </Typography>
          
          {queue.length > 0 && (
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
              {queue.length} пісень у черзі
            </Typography>
          )}
          
          {loading && (
            <LinearProgress sx={{ mt: 1 }} />
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default DailyMix; 