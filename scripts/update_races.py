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
        rock_rock_mountain = db.query(Track).filter(Track.track_name == "Rock Rock Mountain").first()
        dolphin_shoals = db.query(Track).filter(Track.track_name == "Dolphin Shoals").first()

        if not rock_rock_mountain or not dolphin_shoals:
            print("Error: Could not find one or more tracks")
            return

        # Update race 4
        race4 = db.query(Race).filter(Race.race_id == 4).first()
        if race4:
            race4.track_id = rock_rock_mountain.track_id
            print(f"Updated race 4 to Rock Rock Mountain")
        else:
            print("Race 4 not found")

        # Update race 5
        race5 = db.query(Race).filter(Race.race_id == 5).first()
        if race5:
            race5.track_id = dolphin_shoals.track_id
            print(f"Updated race 5 to Dolphin Shoals")
        else:
            print("Race 5 not found")

        db.commit()
        print("\nUpdate complete!")

if __name__ == "__main__":
    update_race_tracks() 