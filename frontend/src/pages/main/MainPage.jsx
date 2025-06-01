import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography } from '@mui/material';
import { useAuth } from '../../features/auth/hooks/useAuth';
import { DailyMix } from '../../features/daily-mix';

export const MainPage = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [favourites, setFavourites] = useState([]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Welcome, {user?.displayName}!
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 3 }}>

      </Typography>
      
      <DailyMix 
        favourites={favourites}
        onPlaySong={() => {}}
        currentSong={null}
        isPlaying={false}
      />
    </Box>
  );
}; 