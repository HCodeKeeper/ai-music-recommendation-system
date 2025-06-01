import {
  Box,
  IconButton,
  InputBase,
  CircularProgress,
  alpha,
} from '@mui/material';
import {
  Search as SearchIcon,
  Close as CloseIcon,
} from '@mui/icons-material';

export const SearchBar = ({
  searchQuery,
  loading,
  onSearchChange,
  onClear,
  placeholder = "Search for songs, artists, or albums...",
  sx = {},
}) => {
  return (
    <Box 
      sx={{ 
        position: 'relative',
        borderRadius: 1,
        bgcolor: (theme) => alpha(theme.palette.common.white, 0.15),
        '&:hover': {
          bgcolor: (theme) => alpha(theme.palette.common.white, 0.25),
        },
        border: 1,
        borderColor: 'divider',
        display: 'flex',
        alignItems: 'center',
        ...sx
      }}
    >
      <IconButton sx={{ p: '10px' }} aria-label="search">
        {loading ? (
          <CircularProgress size={20} />
        ) : (
          <SearchIcon />
        )}
      </IconButton>
      
      <InputBase
        sx={{ 
          ml: 1, 
          flex: 1,
          '& input': {
            padding: '8px 0',
          }
        }}
        placeholder={placeholder}
        value={searchQuery}
        onChange={onSearchChange}
        inputProps={{ 'aria-label': 'search songs' }}
      />
      
      {searchQuery && (
        <IconButton 
          sx={{ p: '10px' }} 
          aria-label="clear search"
          onClick={onClear}
        >
          <CloseIcon />
        </IconButton>
      )}
    </Box>
  );
}; 