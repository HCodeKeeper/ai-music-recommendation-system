import {
  Card,
  CardContent,
  Box,
  Typography,
  IconButton,
} from '@mui/material';
import {
  PlayArrow as PlayArrowIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
  Album as AlbumIcon,
} from '@mui/icons-material';

export const SongCard = ({
  song,
  onPlay,
  onSongClick,
  onLike,
  isLiked = false,
  loading = false,
}) => {
  const handlePlayClick = (e) => {
    e.stopPropagation();
    onPlay?.(song);
  };

  const handleLikeClick = (e) => {
    e.stopPropagation();
    onLike?.(song.id, isLiked);
  };

  const handleCardClick = () => {
    onSongClick?.(song);
  };

  return (
    <Card 
      sx={{ 
        cursor: 'pointer',
        transition: 'transform 0.2s',
        width: 280,
        height: 360,
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0px 2px 1px -1px rgba(0,0,0,0.2), 0px 1px 1px 0px rgba(0,0,0,0.14), 0px 1px 3px 0px rgba(0,0,0,0.12)',
        '&:hover': {
          transform: 'scale(1.02)'
        }
      }}
      onClick={handleCardClick}
    >
      <Box 
        sx={{ 
          position: 'relative',
          width: 280,
          height: 240,
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'background.paper'
        }}
      >
        <AlbumIcon 
          sx={{ 
            fontSize: 100,
            color: 'text.secondary',
            opacity: 0.7
          }} 
        />
      </Box>
      
      <CardContent 
        sx={{ 
          height: 120,
          width: 280,
          p: '16px !important',
          display: 'flex',
          flexDirection: 'row',
          justifyContent: 'space-between',
          alignItems: 'center',
          overflow: 'hidden'
        }}
      >
        <Box 
          sx={{ 
            flex: 1,
            minWidth: 0,
            mr: 2,
            overflow: 'hidden',
            maxWidth: 140
          }}
        >
          <Typography 
            variant="h6" 
            sx={{ 
              fontSize: '1.1rem',
              fontWeight: 600,
              lineHeight: 1.2,
              mb: 0.5,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              maxWidth: 140,
              display: 'flex',
              alignItems: 'center',
              gap: 0.5,
              '&:hover': { 
                textDecoration: 'underline' 
              }
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
            variant="subtitle1"
            sx={{ 
              fontSize: '0.9rem',
              lineHeight: 1.2,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              color: 'text.secondary',
              opacity: 0.9,
              fontWeight: 400,
              maxWidth: 140
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
                maxWidth: 140,
                display: 'block'
              }}
              title={song.genre}
            >
              {song.genre}
            </Typography>
          )}
        </Box>
        
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          <IconButton 
            onClick={handlePlayClick}
            color="primary" 
            size="medium"
            disabled={loading}
            sx={{ 
              flexShrink: 0,
              p: 1,
              width: 48,
              height: 48,
              backgroundColor: 'action.hover',
              '&:hover': {
                backgroundColor: 'primary.main',
                color: 'primary.contrastText'
              }
            }}
          >
            <PlayArrowIcon />
          </IconButton>
          
          <IconButton 
            onClick={handleLikeClick}
            size="medium"
            sx={{ 
              flexShrink: 0,
              p: 1,
              width: 48,
              height: 48,
              color: isLiked ? 'error.main' : 'text.secondary',
              '&:hover': {
                color: 'error.main'
              }
            }}
          >
            {isLiked ? <FavoriteIcon /> : <FavoriteBorderIcon />}
          </IconButton>
        </Box>
      </CardContent>
    </Card>
  );
}; 