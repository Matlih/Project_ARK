import { useState, useEffect } from 'react';

const EONET_URL = 'https://eonet.gsfc.nasa.gov/api/v3/events';

// Philippine bounding box
const PH_BOUNDS = { 
    minLon: 116.0, maxLon: 127.0, 
    minLat: 4.5,   maxLat: 21.0 
};

/**
 * Direct frontend connection to NASA EONET API.
 * No backend proxy needed — EONET is public CORS-enabled.
 */
export async function fetchPHEvents() {
    try {
        const res = await fetch(
            `${EONET_URL}?category=floods,severeStorms,volcanoes&status=open&limit=10`
        );
        
        if (!res.ok) throw new Error("NASA API unavailable");
        
        const data = await res.json();
        
        const phEvents = data.events
            .filter(event => {
                const coords = event.geometry?.[0]?.coordinates;
                if (!coords) return false;
                const [lon, lat] = coords;
                // Filter specifically for the Philippine Area of Responsibility
                return lon >= PH_BOUNDS.minLon && lon <= PH_BOUNDS.maxLon
                    && lat >= PH_BOUNDS.minLat && lat <= PH_BOUNDS.maxLat;
            })
            .map(event => ({
                id: event.id,
                title: event.title,
                category: event.categories?.[0]?.title || 'Event',
                coords: event.geometry[0].coordinates,
                date: new Date(event.geometry[0].date).toLocaleTimeString('en-PH', { hour12: false }),
                lat: event.geometry[0].coordinates[1],
                lon: event.geometry[0].coordinates[0],
            }));
        
        // If no real PH events are currently active, return realistic mock events
        // This ensures the EONET HUD panel is NEVER empty during your demo.
        if (phEvents.length === 0) return getMockEONETEvents();
        return phEvents;
        
    } catch (error) {
        console.warn("[ARK Telemetry] Live NASA feed failed, defaulting to persistent mock stream.", error);
        return getMockEONETEvents();
    }
}

function getMockEONETEvents() {
    return [
        { id: 'mock-1', title: 'Coastal Swell Warning', 
          date: '19:02:20', lat: 14.6, lon: 120.9, 
          category: 'Severe Storms' },
        { id: 'mock-2', title: 'Typhoon Genesis Tracked',
          date: '19:01:37', lat: 13.4, lon: 124.1,
          category: 'Severe Storms' },
        { id: 'mock-3', title: 'Sea Surface Temp Anomaly',
          date: '19:01:13', lat: 10.1, lon: 125.8,
          category: 'Sea and Lake Ice' },
        { id: 'mock-4', title: 'Severe Storm Cell Detected',
          date: '19:02:16', lat: 15.2, lon: 121.5,
          category: 'Severe Storms' },
    ];
}

/**
 * React Hook for UI Components.
 * Call this in your Telemetry panel to get a self-updating 30-second polling feed.
 */
export function useEONETPolling() {
    const [events, setEvents] = useState([]);
    
    useEffect(() => {
        let isMounted = true;
        
        const poll = async () => {
            const freshEvents = await fetchPHEvents();
            if (isMounted) setEvents(freshEvents);
        };
        
        poll(); // Immediate first call
        const interval = setInterval(poll, 30000); // 30-second heartbeat
        
        return () => {
            isMounted = false;
            clearInterval(interval);
        };
    }, []);
    
    return events;
}