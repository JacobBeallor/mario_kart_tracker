import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_context
from models import Race, Track

def update_race_tracks():
    """Update specific races with correct track IDs."""
    with get_db_context() as db:
        # Get track IDs
        new_york_minute = db.query(Track).filter(Track.track_name == "New York Minute").first()

        if not new_york_minute:
            print("Error: Could not find New York Minute track")
            return

        # Update race 11
        race4 = db.query(Race).filter(Race.race_id == 11).first()
        if race4:
            race4.track_id = new_york_minute.track_id
            print(f"Updated race 11 to New York Minute")
        else:
            print("Race 11 not found")

        db.commit()
        print("\nUpdate complete!")

if __name__ == "__main__":
    update_race_tracks() 