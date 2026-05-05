import requests
import json
import os
import re
from pathlib import Path
from datetime import datetime, timedelta

def get_ph_disasters():
    """Fetches open floods and severe storms from EONET, filtered by PH bounding box."""
    url = "https://eonet.gsfc.nasa.gov/api/v3/events"
    params = {
        "category": "floods,severeStorms",
        "status": "open",
        "limit": 5
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        print(f"EONET API Error: {e}")
        return []

    ph_events = []
    for event in data.get('events', []):
        try:
            # EONET coordinates are [longitude, latitude]
            coords = event['geometry'][0]['coordinates']
            lon, lat = coords[0], coords[1]
            
            # PH Bounding Box Check
            if 116.0 <= lon <= 127.0 and 4.5 <= lat <= 21.0:
                ph_events.append(event)
        except (KeyError, IndexError):
            continue
            
    return ph_events

def stage_event_folder(event: dict) -> str:
    """Creates isolated data directory for the event and saves its metadata."""
    event_id = event.get('id', 'unknown_id')
    title = event.get('title', 'Unknown Event')
    
    # Generate clean title slug (lowercase, replace spaces/special chars with underscores)
    title_slug = re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')
    
    # Construct target directory path
    folder_path = Path("data") / "raw" / f"EONET_{event_id}_{title_slug}"
    folder_path.mkdir(parents=True, exist_ok=True)
    
    # Save the raw event JSON into the directory
    json_path = folder_path / "event.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(event, f, indent=4)
        
    return str(folder_path)

def get_sentinel2_query_params(event: dict) -> dict:
    """Generates STAC API query parameters for Sentinel-2 satellite imagery."""
    try:
        coords = event['geometry'][0]['coordinates']
        lon, lat = coords[0], coords[1]
        date_str = event['geometry'][0]['date']
        
        # Extract YYYY-MM-DD from string (e.g., "2024-07-24T00:00:00Z")
        event_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
    except (KeyError, IndexError, ValueError):
        # Fallback if geometry parsing fails
        lon, lat = 121.7, 17.6
        event_date = datetime.utcnow()

    # Create ±7 day window around the event
    start_date = event_date - timedelta(days=7)
    end_date = event_date + timedelta(days=7)
    
    # Generate 0.5 degree buffer for bounding box: [min_lon, min_lat, max_lon, max_lat]
    bbox = [
        round(lon - 0.5, 4),
        round(lat - 0.5, 4),
        round(lon + 0.5, 4),
        round(lat + 0.5, 4)
    ]
    
    return {
        "bbox": bbox,
        "datetime": f"{start_date.strftime('%Y-%m-%d')}T00:00:00Z/{end_date.strftime('%Y-%m-%d')}T23:59:59Z",
        "cloud_cover_max": 30
    }

if __name__ == "__main__":
    print("🛰️ Polling NASA EONET for active Philippine disasters...")
    events = get_ph_disasters()
    
    if not events:
        print("⚠️ No open PH events found or API timed out. Triggering fallback configuration.")
        # Fallback hardcoded event (Typhoon Carina)
        events = [{
            "id": "EONET_FALLBACK_TY_CARINA",
            "title": "Typhoon Carina",
            "categories": [{"id": "severeStorms", "title": "Severe Storms"}],
            "geometry": [{
                "date": "2024-07-24T00:00:00Z",
                "type": "Point",
                "coordinates": [121.7, 17.6]  # [Longitude, Latitude]
            }]
        }]
        
    for event in events:
        print(f"\n--- Processing: {event.get('title')} ---")
        staged_dir = stage_event_folder(event)
        print(f"✅ Data staged at: {staged_dir}")
        
        stac_params = get_sentinel2_query_params(event)
        print("✅ Sentinel-2 STAC Query Parameters:")
        print(json.dumps(stac_params, indent=4))