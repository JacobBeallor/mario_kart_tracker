import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_context
from models import Race, Track, RaceResult

def update_race_tracks():
    """Update specific races with correct track IDs."""
    with get_db_context() as db:
        # Get track IDs
        updated_track = db.query(Track).filter(Track.track_name == "Sydney Sprint").first()
        # Yoshi's Circuit
        #Sydney Sprint
        race_id = 194

        # tracks = db.query(Track)
        # for track in tracks:
        #     print(track.track_name)
        # return

        races = db.query(Race).order_by(Race.created_at)
        for race in races:
            print(race.track.track_name)
            print(race.race_id)
        return
    
        if not updated_track:
            print("Error: Could not find track")
            return
        

        # Update race 16
        race = db.query(Race).filter(Race.race_id == race_id).first()
        if race:
            race.track_id = updated_track.track_id
            print(f"Updated race {race_id} to {updated_track.track_name}")
        else:
            print(f"Race {race_id} not found")

        db.commit()
        print("\nUpdate complete!")

def update_race_results():
    with get_db_context() as db:

        race: RaceResult = db.query(RaceResult).filter(RaceResult.result_id==173).first()
        race.points_earned = 10
        db.commit()
        return
        races: list[RaceResult] = db.query(RaceResult).order_by(RaceResult.created_at.asc()).all()

        for race in races:
            print(race.player.player_nickname)
            print(race.finish_position)
            print(race.race.track.track_name)
            print(race.race.created_at)
            print(race.result_id)
            print(race.points_earned)
            print()

def update_race():
    with get_db_context() as db:

        race = db.query(Race).filter(Race.race_id == 81).first()
        race.track_id = 136

        db.commit()
        return
        print(race.race_id)
        print(race.track.track_id)

        return
        races: list[Race] = db.query(Race).order_by(Race.created_at.asc()).all()

        for race in races:
            print(race.track.track_name)
            print(race.track.track_id)
            print(race.created_at)
            print(race.race_id)
            print()

def check_track():
    with get_db_context() as db:
        track: Track = db.query(Track).filter(Track.track_name=="Donut Plains 3").first()

        print(track.track_id)
        print(track.track_name)

if __name__ == "__main__":
    update_race_tracks() 
    # update_race_results()
    # update_race()
    # check_track()