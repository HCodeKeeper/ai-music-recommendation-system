import {
  Box,
  Typography,
  IconButton,
  Slider,
  Stack,
  CircularProgress,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  SkipNext as SkipNextIcon,
  SkipPrevious as SkipPreviousIcon,
  VolumeUp as VolumeUpIcon,
} from '@mui/icons-material';

export const PlayerControls = ({
  currentSong,
  isPlaying,
  progress,
  currentTime,
  duration,
  volume,
  loading,
  onPlayPause,
  onProgressChange,
  onVolumeChange,
  onPrevious,
  onNext,
  formatTime,
}) => {
  if (!currentSong) {
    return null;
  }

  return (
    <Box
      sx={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        bgcolor: 'background.paper',
        borderTop: 1,
        borderColor: 'divider',
        p: 2,
        display: 'flex',
        alignItems: 'center',
        gap: 2,
        zIndex: 1000,
      }}
    >
      {/* Song Info */}
      <Box sx={{ minWidth: 200, maxWidth: 300 }}>
        <Typography variant="subtitle2" noWrap>
          {currentSong.name}
        </Typography>
        <Typography variant="caption" color="text.secondary" noWrap>
          {currentSong.artist}
        </Typography>
      </Box>

      {/* Main Controls */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        {/* Control Buttons */}
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
          <IconButton onClick={onPrevious} size="small">
            <SkipPreviousIcon />
          </IconButton>
          
          <IconButton
            onClick={() => onPlayPause(currentSong)}
            disabled={loading}
            sx={{
              bgcolor: 'primary.main',
              color: 'white',
              width: 40,
              height: 40,
              '&:hover': {
                bgcolor: 'primary.dark',
              },
              '&:disabled': {
                bgcolor: 'action.disabled',
              },
            }}
          >
            {loading ? (
              <CircularProgress size={20} color="inherit" />
            ) : isPlaying ? (
              <PauseIcon />
            ) : (
              <PlayIcon />
            )}
          </IconButton>
          
          <IconButton onClick={onNext} size="small">
            <SkipNextIcon />
          </IconButton>
        </Stack>

        {/* Progress Bar */}
        <Stack direction="row" spacing={1} alignItems="center" sx={{ width: '100%', maxWidth: 400 }}>
          <Typography variant="caption" sx={{ minWidth: 40 }}>
            {formatTime(currentTime)}
          </Typography>
          
          <Slider
            value={progress}
            onChange={onProgressChange}
            sx={{
              flex: 1,
              '& .MuiSlider-thumb': {
                width: 12,
                height: 12,
              },
              '& .MuiSlider-track': {
                height: 4,
              },
              '& .MuiSlider-rail': {
                height: 4,
                opacity: 0.3,
              },
            }}
          />
          
          <Typography variant="caption" sx={{ minWidth: 40 }}>
            {formatTime(duration)}
          </Typography>
        </Stack>
      </Box>

      {/* Volume Control */}
      <Box sx={{ minWidth: 120, display: 'flex', alignItems: 'center', gap: 1 }}>
        <VolumeUpIcon fontSize="small" />
        <Slider
          value={volume}
          onChange={onVolumeChange}
          sx={{
            width: 80,
            '& .MuiSlider-thumb': {
              width: 12,
              height: 12,
            },
            '& .MuiSlider-track': {
              height: 3,
            },
            '& .MuiSlider-rail': {
              height: 3,
              opacity: 0.3,
            },
          }}
        />
      </Box>
    </Box>
  );
}; 