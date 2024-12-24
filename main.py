from database import get_db_context, init_db
from models import Player, Track, Prix, Race, RaceResult, KartCombo
from datetime import datetime

def create_sample_data():
    with get_db_context() as db:
        # Create players
        players = [
            Player(
                player_first_name="Mario",
                player_last_name="Mario",
                player_nickname="Super Mario"
            ),
            Player(
                player_first_name="Luigi",
                player_last_name="Mario",
                player_nickname="Green Mario"
            ),
            Player(
                player_first_name="Princess",
                player_last_name="Peach",
                player_nickname="Peach"
            ),
            Player(
                player_first_name="Yoshi",
                player_last_name="Dinosaur",
                player_nickname="Yoshi"
            ),
        ]
        db.add_all(players)

        # Create tracks with their cups
        tracks = [
            Track(track_name="Mario Kart Stadium", cup_name="Mushroom Cup"),
            Track(track_name="Water Park", cup_name="Mushroom Cup"),
            Track(track_name="Sweet Sweet Canyon", cup_name="Mushroom Cup"),
            Track(track_name="Thwomp Ruins", cup_name="Mushroom Cup"),
            Track(track_name="Mario Circuit", cup_name="Flower Cup"),
            Track(track_name="Toad Harbor", cup_name="Flower Cup"),
            Track(track_name="Twisted Mansion", cup_name="Flower Cup"),
            Track(track_name="Shy Guy Falls", cup_name="Flower Cup"),
        ]
        db.add_all(tracks)

        # Create kart combinations
        kart_combos = [
            KartCombo(
                character_name="Mario",
                vehicle_name="Standard Kart",
                tire_name="Standard",
                glider_name="Super Glider"
            ),
            KartCombo(
                character_name="Luigi",
                vehicle_name="Pipe Frame",
                tire_name="Monster",
                glider_name="Parafoil"
            ),
            KartCombo(
                character_name="Peach",
                vehicle_name="Cat Cruiser",
                tire_name="Roller",
                glider_name="Flower Glider"
            ),
            KartCombo(
                character_name="Yoshi",
                vehicle_name="Sport Bike",
                tire_name="Slick",
                glider_name="Cloud Glider"
            ),
        ]
        db.add_all(kart_combos)

        # Create a Grand Prix
        mushroom_cup_prix = Prix(
            prix_type="grand_prix",
            cup_name="Mushroom Cup",
            number_of_players=4,
            cc_class=150,
            is_mirror_mode=False,
            is_teams_mode=False,
            items_setting="normal",
            com_level="normal",
            com_vehicles="all",
            courses_setting="in_order",
            race_count=4,
            date_played=datetime.utcnow()
        )
        db.add(mushroom_cup_prix)
        db.flush()  # Flush to get the prix_id

        # Create races for the Grand Prix
        for i, track in enumerate(tracks[:4], 1):  # First 4 tracks (Mushroom Cup)
            race = Race(
                prix_id=mushroom_cup_prix.prix_id,
                track_id=track.track_id,
                race_number=i
            )
            db.add(race)
            db.flush()  # Flush to get the race_id

            # Add race results for each player
            for j, (player, combo) in enumerate(zip(players, kart_combos), 1):
                result = RaceResult(
                    race_id=race.race_id,
                    player_id=player.player_id,
                    combo_id=combo.combo_id,
                    finish_position=j,
                    points_earned=16 - j  # Simple point calculation
                )
                db.add(result)

def main():
    print("Initializing database...")
    init_db()
    
    print("Creating sample data...")
    create_sample_data()
    
    print("Sample data created successfully!")

if __name__ == "__main__":
    main() 