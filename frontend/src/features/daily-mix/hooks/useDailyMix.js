

import { useState, useRef, useCallback, useEffect } from 'react';
import { apiClient } from '../../../shared/api';

const BATCH_SIZE = 7;         

export default function useDailyMix(favourites = [], likedSongIds = []) {

    const seedStack   = useRef([...favourites].reverse());   //
    const playQueue   = useRef([]);                         
    const playedSet   = useRef(new Set());              
    const skippedSet  = useRef(new Set());                 
    const playHistory = useRef([]);                         

    
    const [current, setCurrent]     = useState(null);
    const [queueSnapshot, setSnap]  = useState([]);  
    const [done, setDone]           = useState(false);
    const [loading, setLoading]     = useState(false);
    const [error, setError]         = useState(null);
    const [currentSeedInfo, setCurrentSeedInfo] = useState(null);
    const [historyIndex, setHistoryIndex] = useState(-1); 


    const getAllExcludedIds = useCallback(() => {

        return [
            ...Array.from(playedSet.current),
            ...Array.from(skippedSet.current),
            ...likedSongIds.map(id => String(id)) 
        ];
    }, [likedSongIds]);

    const fetchBatch = async (seedId) => {
        try {
            setError(null);
            const excludeIds = getAllExcludedIds();
            

            console.log(`Fetching batch for seed ${seedId}, excluding ${excludeIds.length} tracks`);
            
            const { data } = await apiClient.music.getDailyMix(excludeIds, seedId);
            
            if (!data.recommendations || data.recommendations.length === 0) {
                console.log('No recommendations returned from backend');
                return [];
            }


            if (data.seed_song) {
                setCurrentSeedInfo(data.seed_song);
            }


            const filtered = data.recommendations.filter(track => 
                !playedSet.current.has(String(track.id)) && 
                !skippedSet.current.has(String(track.id))
            );

            console.log(`Got ${data.recommendations.length} recommendations, ${filtered.length} after filtering`);
            return filtered;
            
        } catch (e) {
            const errorMsg = e.response?.data?.message || e.message || 'Failed to fetch recommendations';
            setError(errorMsg);
            console.error('Error fetching daily mix batch:', errorMsg);
            return [];
        }
    };

    const fillQueueIfEmpty = useCallback(async () => {
        while (playQueue.current.length === 0 && seedStack.current.length > 0) {
            const seedId = seedStack.current.pop();
            console.log(`Using seed ${seedId} from stack`);
            const batch = await fetchBatch(seedId);
            playQueue.current.push(...batch);
        }
        setSnap([...playQueue.current]);
        if (playQueue.current.length === 0 && seedStack.current.length === 0) {
            setDone(true);
        }
    }, [fetchBatch]);


    const next = useCallback(async () => {
        if (done || loading) return;

        if (historyIndex >= 0 && historyIndex < playHistory.current.length - 1) {
 
            const newIndex = historyIndex + 1;
            setHistoryIndex(newIndex);
            setCurrent(playHistory.current[newIndex]);
            return;
        }
        

        setLoading(true);
        try {
            await fillQueueIfEmpty();
            const nextTrack = playQueue.current.shift();
            if (nextTrack) {

                if (current && (playHistory.current.length === 0 || playHistory.current[playHistory.current.length - 1].id !== current.id)) {
                    playHistory.current.push(current);
                }
                
                playedSet.current.add(String(nextTrack.id));
                setCurrent(nextTrack);
                setSnap([...playQueue.current]);
                setHistoryIndex(-1);
                

                playHistory.current.push(nextTrack);
            } else {
                setDone(true);
            }
        } finally {
            setLoading(false);
        }
    }, [done, loading, fillQueueIfEmpty, current, historyIndex]);

    const likeCurrent = useCallback(async () => {
        if (!current) return;
        
        console.log(`Liked track: ${current.name} - ${current.artist}`);
        
        // Add liked track as a new seed (highest priority)
        // Place it at the end of the stack so it's used next (LIFO)
        seedStack.current.push(String(current.id));
        
        // Optionally add to user's preferences via API
        try {
            await apiClient.preferences.addPreference(current.id);
            console.log('Added liked track to user preferences');
        } catch (e) {
            console.warn('Failed to add to preferences:', e.response?.data?.message || e.message);
            // Continue anyway - the local seed stack addition is more important for immediate experience
        }
        
        await next();
    }, [current, next]);

    const skipCurrent = useCallback(async () => {
        if (!current) return;
        
        console.log(`Skipped track: ${current.name} - ${current.artist}`);
        
        // Add to skipped set to avoid recommending again
        skippedSet.current.add(String(current.id));
        
        await next();
    }, [current, next]);

    const previous = useCallback(() => {
        if (playHistory.current.length === 0) return;
        
        // If we're in live mode (historyIndex = -1), go to the previous track
        if (historyIndex === -1) {
            if (playHistory.current.length >= 2) {
                // Go to the second-to-last track (since the last one is current)
                const newIndex = playHistory.current.length - 2;
                setHistoryIndex(newIndex);
                setCurrent(playHistory.current[newIndex]);
            }
        } else if (historyIndex > 0) {
            // Go back one more track in history
            const newIndex = historyIndex - 1;
            setHistoryIndex(newIndex);
            setCurrent(playHistory.current[newIndex]);
        }
        // If historyIndex is 0, we're at the beginning of history, do nothing
    }, [historyIndex]);

    const reset = useCallback(() => {
        // Reset all state for a fresh daily mix session
        seedStack.current = [...favourites].reverse();
        playQueue.current = [];
        playedSet.current.clear();
        skippedSet.current.clear();
        playHistory.current = [];
        setCurrent(null);
        setSnap([]);
        setDone(false);
        setError(null);
        setCurrentSeedInfo(null);
        setHistoryIndex(-1);
    }, [favourites]);

    //   Kick‑off first track once favourites arrive
    useEffect(() => {
        if (current === null && !done && !loading && favourites.length > 0) {
            console.log('Starting daily mix with', favourites.length, 'favourite seeds');
            next();
        }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [favourites]);

    return {
        // Current state
        currentTrack: current,
        queue: queueSnapshot,
        currentSeed: currentSeedInfo,
        loading,
        error,
        done,
        
        // Stats for UI
        seedsRemaining: seedStack.current.length,
        tracksPlayed: playedSet.current.size,
        tracksSkipped: skippedSet.current.size,
        historyLength: playHistory.current.length,
        canGoBack: historyIndex > 0 || (historyIndex === -1 && playHistory.current.length >= 2),
        canGoForward: historyIndex >= 0 && historyIndex < playHistory.current.length - 1,
        
        // Controls
        next,
        likeCurrent,
        skipCurrent,
        previous,
        reset
    };
} 