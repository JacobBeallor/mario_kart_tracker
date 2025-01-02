import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_context
from models import Track

TRACKS = {
    "Mushroom Cup": [
        "Mario Kart Stadium",
        "Water Park",
        "Sweet Sweet Canyon",
        "Thwomp Ruins"
    ],
    "Flower Cup": [
        "Mario Circuit",
        "Toad Harbor",
        "Twisted Mansion",
        "Shy Guy Falls"
    ],
    "Star Cup": [
        "Sunshine Airport",
        "Dolphin Shoals",
        "Electrodrome",
        "Mount Wario"
    ],
    "Special Cup": [
        "Cloudtop Cruise",
        "Bone-Dry Dunes",
        "Bowser's Castle",
        "Rainbow Road"
    ],
    "Shell Cup": [
        "Moo Moo Meadows",
        "Mario Circuit (GBA)",
        "Cheep Cheep Beach",
        "Toad's Turnpike"
    ],
    "Banana Cup": [
        "Dry Dry Desert",
        "Donut Plains 3",
        "Royal Raceway",
        "DK Jungle"
    ],
    "Leaf Cup": [
        "Wario Stadium",
        "Sherbet Land",
        "Music Park",
        "Yoshi Valley"
    ],
    "Lightning Cup": [
        "Tick-Tock Clock",
        "Piranha Plant Slide",
        "Grumble Volcano",
        "Rainbow Road (N64)"
    ],
    "Egg Cup": [
        "Yoshi's Circuit",
        "Excitebike Arena",
        "Dragon Driftway",
        "Mute City"
    ],
    "Triforce Cup": [
        "Wario's Gold Mine",
        "Rainbow Road (SNES)",
        "Ice Ice Outpost",
        "Hyrule Circuit"
    ],
    "Bell Cup": [
        "Neo Bowser City",
        "Ribbon Road",
        "Super Bell Subway",
        "Big Blue"
    ],
    "Crossing Cup": [
        "Baby Park",
        "Cheese Land",
        "Wild Woods",
        "Animal Crossing"
    ],
    "Golden Dash Cup": [
        "Paris Promenade",
        "Toad Circuit",
        "Choco Mountain",
        "Coconut Mall"
    ],
    "Lucky Cat Cup": [
        "Tokyo Blur",
        "Shroom Ridge",
        "Sky Garden",
        "Ninja Hideaway"
    ],
    "Turnip Cup": [
        "New York Minute",
        "Mario Circuit 3",
        "Kalimari Desert",
        "Waluigi Pinball"
    ],
    "Propeller Cup": [
        "Sydney Sprint",
        "Snow Land",
        "Mushroom Gorge",
        "Sky-High Sundae"
    ],
    "Rock Cup": [
        "London Loop",
        "Boo Lake",
        "Rock Rock Mountain",
        "Maple Treeway"
    ],
    "Moon Cup": [
        "Berlin Byways",
        "Peach Gardens",
        "Merry Mountain",
        "Rainbow Road (3DS)"
    ],
    "Fruit Cup": [
        "Amsterdam Drift",
        "Riverside Park",
        "DK Summit",
        "Yoshi's Island"
    ],
    "Boomerang Cup": [
        "Bangkok Rush",
        "Mario Circuit (DS)",
        "Waluigi Stadium",
        "Singapore Speedway"
    ],
    "Feather Cup": [
        "Athens Dash",
        "Daisy Cruiser",
        "Moonview Highway",
        "Squeaky Clean Sprint"
    ],
    "Cherry Cup": [
        "Los Angeles Laps",
        "Sunset Wilds",
        "Koopa Cape",
        "Vancouver Velocity"
    ],
    "Acorn Cup": [
        "Rome Avanti",
        "DK Mountain",
        "Daisy Circuit",
        "Piranha Plant Cove"
    ],
    "Spiny Cup": [
        "Madrid Drive",
        "Rosalina's Ice World",
        "Bowser Castle 3",
        "Rainbow Road (Wii)"
    ]
}

def populate_tracks():
    """Add all Mario Kart 8 Deluxe tracks to the database."""
    print("Starting track population...")
    
    with get_db_context() as db:
        # Get existing tracks to avoid duplicates
        existing_tracks = {
            track.track_name for track in 
            db.query(Track.track_name).all()
        }
        
        tracks_added = 0
        
        for cup_name, tracks in TRACKS.items():
            for track_name in tracks:
                if track_name not in existing_tracks:
                    track = Track(
                        track_name=track_name,
                        cup_name=cup_name
                    )
                    db.add(track)
                    tracks_added += 1
                    print(f"Added: {track_name} ({cup_name})")
        
        db.commit()
        print(f"\nPopulation complete! Added {tracks_added} new tracks.")

if __name__ == "__main__":
    populate_tracks() 