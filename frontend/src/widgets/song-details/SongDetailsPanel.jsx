import {
  Box,
  Typography,
  IconButton,
  Chip,
  Stack,
  Divider,
  CircularProgress,
  Paper,
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';

export const SongDetailsPanel = ({
  song,
  open,
  onClose,
  loading = false,
  songDetails = null,
}) => {
  if (!open || !song) {
    return null;
  }

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 64, // Below the app bar
        right: 0,
        width: 400,
        height: 'calc(100vh - 64px)',
        bgcolor: 'background.paper',
        borderLeft: 1,
        borderColor: 'divider',
        zIndex: 1200,
        overflow: 'auto',
      }}
    >
      <Paper
        elevation={0}
        sx={{
          height: '100%',
          borderRadius: 0,
          p: 3,
        }}
      >
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6">Song Details</Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Stack spacing={3}>
            {/* Basic Info */}
            <Box>
              <Typography variant="h5" gutterBottom>
                {song.name}
              </Typography>
              <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                {song.artist}
              </Typography>
              {song.genre && (
                <Chip
                  label={song.genre}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              )}
            </Box>

            <Divider />

            {/* Song Attributes */}
            <Box>
              <Typography variant="h6" gutterBottom>
                Song Information
              </Typography>
              <Stack spacing={1}>
                {song.id && (
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">
                      Track ID:
                    </Typography>
                    <Typography variant="body2">{song.id}</Typography>
                  </Box>
                )}
                
                {song.pathToTrack && (
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">
                      Audio Available:
                    </Typography>
                    <Typography variant="body2" color="success.main">
                      Yes
                    </Typography>
                  </Box>
                )}

                {song.album && (
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">
                      Album:
                    </Typography>
                    <Typography variant="body2">{song.album}</Typography>
                  </Box>
                )}

                {song.year && (
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">
                      Year:
                    </Typography>
                    <Typography variant="body2">{song.year}</Typography>
                  </Box>
                )}
              </Stack>
            </Box>

            {/* Song Details from API */}
            {songDetails && (
              <>
                <Divider />
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Musical Tags
                  </Typography>
                  {songDetails.genres?.length > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Genres:
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {songDetails.genres.map((genre, index) => (
                          <Chip
                            key={index}
                            label={genre}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </Box>
                  )}

                  {songDetails.tags && Object.keys(songDetails.tags).length > 0 && (
                    <Box>
                      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                        Attributes:
                      </Typography>
                      <Stack spacing={1}>
                        {Object.entries(songDetails.tags).map(([key, value]) => (
                          <Box key={key} sx={{ display: 'flex', justifyContent: 'space-between' }}>
                            <Typography variant="body2" color="text.secondary">
                              {key}:
                            </Typography>
                            <Typography variant="body2">{value}</Typography>
                          </Box>
                        ))}
                      </Stack>
                    </Box>
                  )}
                </Box>

                {/* Recommendation Reason */}
                {songDetails.recommendationReason && (
                  <>
                    <Divider />
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        Why This Song?
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {songDetails.recommendationReason}
                      </Typography>
                    </Box>
                  </>
                )}
              </>
            )}

            {/* Help Text */}
            <Box sx={{ mt: 'auto', pt: 2 }}>
              <Typography variant="caption" color="text.secondary">
                Click on any song to see detailed information and recommendations.
              </Typography>
            </Box>
          </Stack>
        )}
      </Paper>
    </Box>
  );
}; 