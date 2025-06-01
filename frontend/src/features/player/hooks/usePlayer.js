import { useState, useEffect, useRef, useCallback } from 'react';

export const usePlayer = () => {
  const [currentSong, setCurrentSong] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(25);
  const [loading, setLoading] = useState(false);
  const [currentQueue, setCurrentQueue] = useState([]);
  const audioRef = useRef(new Audio());


  const formatTime = useCallback((seconds) => {
    if (!seconds || isNaN(seconds) || seconds === 0) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }, []);


  useEffect(() => {
    const audio = audioRef.current;

    const handleTimeUpdate = () => {
      if (audio.duration) {
        const progressPercent = (audio.currentTime / audio.duration) * 100;
        setProgress(progressPercent);
        setCurrentTime(audio.currentTime);
      }
    };

    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
      setLoading(false);
    };

    const handleCanPlay = () => {
      setLoading(false);
    };

    const handleLoadStart = () => {
      setLoading(true);
    };

    const handleLoadedData = () => {
      setLoading(false);
    };

    const handlePlay = () => {
      setIsPlaying(true);
    };

    const handlePause = () => {
      setIsPlaying(false);
    };

    const handleEnded = () => {
      setIsPlaying(false);
      handleNext();
    };

    const handleError = (e) => {
      console.error('Audio playback error:', e);
      setLoading(false);
      setIsPlaying(false);
    };


    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('canplay', handleCanPlay);
    audio.addEventListener('loadstart', handleLoadStart);
    audio.addEventListener('loadeddata', handleLoadedData);
    audio.addEventListener('play', handlePlay);
    audio.addEventListener('pause', handlePause);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);


    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('canplay', handleCanPlay);
      audio.removeEventListener('loadstart', handleLoadStart);
      audio.removeEventListener('loadeddata', handleLoadedData);
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('pause', handlePause);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);
    };
  }, []);


  useEffect(() => {
    audioRef.current.volume = volume / 100;
  }, [volume]);


  const handlePlayPause = useCallback(async (song) => {
    try {
      if (currentSong?.id === song.id) {

        if (isPlaying) {
          audioRef.current.pause();
        } else {
          await audioRef.current.play();
        }
      } else {

        setLoading(true);
        setCurrentSong(song);
        
        if (song.pathToTrack) {

          const baseUrl = 'http://localhost:5000';
          const audioUrl = `${baseUrl}/api/music/file/${song.id}`;
          audioRef.current.src = audioUrl;
          await audioRef.current.play();
        } else {
          console.warn('Song has no audio file path:', song);
          setLoading(false);
        }
      }
    } catch (error) {
      console.error('Error playing song:', error);
      setLoading(false);
      setIsPlaying(false);
    }
  }, [currentSong, isPlaying]);


  const handleProgressChange = useCallback((_, newValue) => {
    const audio = audioRef.current;
    if (audio.duration) {
      const newTime = (newValue / 100) * audio.duration;
      audio.currentTime = newTime;
      setProgress(newValue);
      setCurrentTime(newTime);
    }
  }, []);


  const handleVolumeChange = useCallback((_, newValue) => {
    setVolume(newValue);
  }, []);


  const handlePrevious = useCallback(() => {
    if (!currentQueue.length || !currentSong) return;
    
    const currentIndex = currentQueue.findIndex(song => song.id === currentSong.id);
    if (currentIndex > 0) {
      const previousSong = currentQueue[currentIndex - 1];
      handlePlayPause(previousSong);
    } else if (currentIndex === 0) {

      const lastSong = currentQueue[currentQueue.length - 1];
      handlePlayPause(lastSong);
    }
  }, [currentQueue, currentSong, handlePlayPause]);


  const handleNext = useCallback(() => {
    if (!currentQueue.length || !currentSong) return;
    
    const currentIndex = currentQueue.findIndex(song => song.id === currentSong.id);
    if (currentIndex < currentQueue.length - 1) {
      const nextSong = currentQueue[currentIndex + 1];
      handlePlayPause(nextSong);
    } else if (currentIndex === currentQueue.length - 1) {

      const firstSong = currentQueue[0];
      handlePlayPause(firstSong);
    }
  }, [currentQueue, currentSong, handlePlayPause]);


  const setQueue = useCallback((newQueue) => {
    setCurrentQueue(newQueue);
  }, []);

  const addToQueue = useCallback((song) => {
    setCurrentQueue(prev => [...prev, song]);
  }, []);

  const removeFromQueue = useCallback((songId) => {
    setCurrentQueue(prev => prev.filter(song => song.id !== songId));
  }, []);

  return {

    currentSong,
    isPlaying,
    progress,
    currentTime,
    duration,
    volume,
    loading,
    currentQueue,
    

    handlePlayPause,
    handleProgressChange,
    handleVolumeChange,
    handlePrevious,
    handleNext,
    

    setQueue,
    addToQueue,
    removeFromQueue,
    

    formatTime,
    

    audioRef,
  };
}; 