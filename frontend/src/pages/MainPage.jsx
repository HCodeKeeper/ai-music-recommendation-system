import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Drawer,
  Button,
  CssBaseline,
} from '@mui/material';


import { useAuth } from '../features/auth/hooks/useAuth';
import { usePlayer } from '../features/player/hooks/usePlayer';
import { useSearch } from '../features/search/hooks/useSearch';
import { useFavorites } from '../features/favorites/hooks/useFavorites';
import useDailyMix from '../features/daily-mix/hooks/useDailyMix';
import { useTagBrowser } from '../features/tag-browser/hooks/useTagBrowser';


import { PlayerControls } from '../widgets/player-controls/PlayerControls';
import { MusicBrowser } from '../widgets/music-browser/MusicBrowser';
import { SongDetailsPanel } from '../widgets/song-details/SongDetailsPanel';


import { SearchBar } from '../features/search/ui/SearchBar';


import { apiClient } from '../shared/api';
import { t } from '../shared/lib/translations';

const DRAWER_WIDTH = 240;

export const MainPage = ({ user, onLogout, onNeedsColdStart }) => {
  const navigate = useNavigate();
  const [selectedSong, setSelectedSong] = useState(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [error, setError] = useState(null);
  const [songDetailsLoading, setSongDetailsLoading] = useState(false);
  const [songDetails, setSongDetails] = useState(null);


  const { logout } = useAuth();
  
  const {
    currentSong,
    isPlaying,
    progress,
    currentTime,
    duration,
    volume,
    currentQueue,
    loading: playerLoading,
    handlePlayPause,
    handleProgressChange,
    handleVolumeChange,
    handlePrevious,
    handleNext,
    setQueue,
    formatTime,
  } = usePlayer();

  const {
    searchQuery,
    searchResults,
    isSearchMode,
    loading: searchLoading,
    error: searchError,
    search,
    clearSearch,
  } = useSearch();

  const {
    likedSongs,
    favouritesPlaylist,
    loading: favoritesLoading,
    error: favoritesError,
    handleLike,
    isSongLiked,
    refreshFavorites,
  } = useFavorites();

  const {
    currentTrack: dailyMixCurrentTrack,
    queue: dailyMixQueue,
    loading: dailyMixLoading,
    error: dailyMixError,
    done: dailyMixDone,
    tracksPlayed,
    next: dailyMixNext,
    likeCurrent: dailyMixLikeCurrent,
    skipCurrent: dailyMixSkipCurrent,
    previous: dailyMixPrevious,
    reset: dailyMixReset,
  } = useDailyMix(
    favouritesPlaylist?.songs?.map(s => s.id || s.song_id) || [],
    Array.from(likedSongs)
  );

  const {
    loading: tagBrowserLoading,
    error: tagBrowserError,
    handleTagPlay,
    clearError: clearTagError,
  } = useTagBrowser();


  useEffect(() => {
    if (dailyMixCurrentTrack && dailyMixCurrentTrack.id !== currentSong?.id) {
      const newQueue = [dailyMixCurrentTrack, ...dailyMixQueue];
      setQueue(newQueue);
      handlePlayPause(dailyMixCurrentTrack);
    }
  }, [dailyMixCurrentTrack, currentSong?.id, dailyMixQueue, setQueue, handlePlayPause]);


  const checkColdStartError = (error) => {
    if (error.response?.data?.needs_cold_start) {
      console.log('API indicates user needs cold start, redirecting...');
      onNeedsColdStart();
      return true;
    }
    return false;
  };


  const handleLogout = () => {
    logout();
    onLogout();
    navigate('/login');
  };

  const handleSongClick = async (song, withRecommendation = false) => {
    try {
      setSelectedSong(song);
      setDetailsOpen(true);
      setSongDetails(null);
      
      if (withRecommendation) {

        setSongDetailsLoading(true);
        try {

          const mockSongDetails = {
            genres: ["Rock", "Alternative", "Indie"],
            tags: {
              "Mood": "Energetic",
              "Era": "2000s",
              "BPM": "120",
              "Key": "C Major",
              "Energy": "High",
              "Danceability": "Medium"
            },
            recommendationReason: `Based on your listening to similar songs. This track matches your preference for ${song.genre || 'this genre'} music.`
          };
          setSongDetails(mockSongDetails);
        } catch (err) {
          console.error('Failed to fetch song details:', err);
        } finally {
          setSongDetailsLoading(false);
        }
      }
    } catch (err) {
      console.error('Failed to handle song click:', err);
      setError('Failed to load song details');
    }
  };

  const handleSongPlay = async (song) => {
    try {
      await handlePlayPause(song);
    } catch (err) {
      console.error('Failed to play song:', err);
      if (!checkColdStartError(err)) {
        setError('Failed to play song');
      }
    }
  };

  const handleSearchSongPlay = async (song) => {
    try {

      setQueue(searchResults);
      await handlePlayPause(song);
    } catch (err) {
      console.error('Failed to play search song:', err);
      if (!checkColdStartError(err)) {
        setError('Failed to play song');
      }
    }
  };

  const handleTagPlayAction = async (tag) => {
    await handleTagPlay(tag, handleSongPlay, setQueue);
  };

  const handleDailyMixClick = async () => {
    try {
      if (dailyMixCurrentTrack) {

        await handlePlayPause(dailyMixCurrentTrack);
      } else if (dailyMixDone) {

        dailyMixReset();
      } else {

        await dailyMixNext();
      }
    } catch (err) {
      console.error('Failed to handle daily mix click:', err);
      if (!checkColdStartError(err)) {
        setError('Failed to start Daily Mix');
      }
    }
  };

  const handleErrorClose = () => {
    setError(null);
  };

  const handleDetailsClose = () => {
    setDetailsOpen(false);
    setSelectedSong(null);
    setSongDetails(null);
  };


  const combinedError = error || searchError || favoritesError || tagBrowserError;

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      <CssBaseline />
      
      {/* Top App Bar */}
      <AppBar 
        position="fixed" 
        sx={{ 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          backgroundColor: 'background.paper',
          borderBottom: '1px solid',
          borderBottomColor: 'divider',
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Typography variant="h6" noWrap component="div" sx={{ color: 'text.primary' }}>
            Music Recommendations
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1, justifyContent: 'center' }}>
            <SearchBar
              searchQuery={searchQuery}
              onSearch={search}
              onClear={clearSearch}
              loading={searchLoading}
            />
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
              {user?.name || user?.email}
            </Typography>
            <Button 
              color="inherit" 
              onClick={handleLogout}
              sx={{ color: 'text.primary' }}
            >
              {t('logout')}
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          height: '100vh',
          overflow: 'hidden',
          marginRight: detailsOpen ? '400px' : 0,
          transition: 'margin-right 0.3s ease',
        }}
      >
        <MusicBrowser
          searchMode={isSearchMode}
          searchQuery={searchQuery}
          searchResults={searchResults}
          searchLoading={searchLoading}
          onSongPlay={isSearchMode ? handleSearchSongPlay : handleSongPlay}
          onSongClick={(song) => handleSongClick(song, true)}
          onSongLike={handleLike}
          onTagPlay={handleTagPlayAction}
          onDailyMixClick={handleDailyMixClick}
          isLiked={isSongLiked}
          error={combinedError}
          onErrorClose={handleErrorClose}
          dailyMixData={{
            currentTrack: dailyMixCurrentTrack,
            done: dailyMixDone,
            error: dailyMixError,
            loading: dailyMixLoading,
            tracksPlayed,
          }}
          favouritesPlaylist={favouritesPlaylist}
        />
      </Box>

      {/* Song Details Panel */}
      <SongDetailsPanel
        song={selectedSong}
        open={detailsOpen}
        onClose={handleDetailsClose}
        loading={songDetailsLoading}
        songDetails={songDetails}
      />

      {/* Bottom Player Controls */}
      {currentSong && (
        <PlayerControls
          currentSong={currentSong}
          isPlaying={isPlaying}
          progress={progress}
          currentTime={currentTime}
          duration={duration}
          volume={volume}
          loading={playerLoading}
          onPlayPause={() => handlePlayPause(currentSong)}
          onNext={handleNext}
          onPrevious={handlePrevious}
          onProgressChange={handleProgressChange}
          onVolumeChange={handleVolumeChange}
          formatTime={formatTime}
        />
      )}
    </Box>
  );
}; 