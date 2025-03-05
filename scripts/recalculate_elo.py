import os
import sys
from datetime import datetime

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_context
from models import Player, Prix, Race, RaceResult, PrixResult
from sqlalchemy import func
from elo import calculate_elo_adjustments, apply_elo_adjustments

DEFAULT_ELO = 1500

def reset_elo_ratings(player_ratings: dict[str, int] = None):
    """Reset players' ELO ratings to specified values.
    
    Args:
        player_ratings: Dict mapping player nicknames to their new ratings.
                       If None, resets all players to DEFAULT_ELO.
    """
    with get_db_context() as db:
        if player_ratings is None:
            # Reset all players to default
            db.query(Player).update({"elo_rating": DEFAULT_ELO})
            print(f"Reset all players to {DEFAULT_ELO} ELO")
        else:
            # Update each player's rating individually
            for nickname, rating in player_ratings.items():
                player = db.query(Player).filter(Player.player_nickname == nickname).first()
                if player:
                    player.elo_rating = rating
                    print(f"Reset {nickname} to {rating} ELO")
                else:
                    print(f"Warning: Player {nickname} not found")
        db.commit()

def recalculate_elo_ratings():
    """Recalculate ELO ratings by processing all prix in chronological order."""
    with get_db_context() as db:
        # Get all prix ordered by date
        prix_list = (
            db.query(Prix)
            .order_by(Prix.date_played)
            .all()
        )

        print(f"Found {len(prix_list)} prix to process")

        for prix in prix_list:
            print(f"\nProcessing prix {prix.prix_id} from {prix.date_played}")

            # Get prix results
            prix_results = (
                db.query(
                    Player.player_nickname,
                    Player.elo_rating,
                    func.sum(RaceResult.points_earned).label('total_points')
                )
                .join(RaceResult, Player.player_id == RaceResult.player_id)
                .join(Race, RaceResult.race_id == Race.race_id)
                .filter(Race.prix_id == prix.prix_id)
                .group_by(Player.player_nickname, Player.elo_rating)
                .all()
            )

            if not prix_results:
                print(f"No results found for prix {prix.prix_id}, skipping...")
                continue

            # Calculate placements
            sorted_results = sorted(
                prix_results,
                key=lambda x: x.total_points,
                reverse=True
            )

            # Create placements list and current ratings dict
            placements = []
            current_ratings = {}
            current_placement = 1
            current_points = sorted_results[0].total_points

            for result in sorted_results:
                if result.total_points < current_points:
                    current_points = result.total_points
                    current_placement = len(placements) + 1

                placements.append((result.player_nickname, current_placement))
                current_ratings[result.player_nickname] = result.elo_rating

            # Calculate and apply ELO adjustments
            elo_adjustments = calculate_elo_adjustments(placements, current_ratings)
            new_ratings = apply_elo_adjustments(current_ratings, elo_adjustments)

            # Update database with new ratings
            for player_nickname, new_rating in new_ratings.items():
                db.query(Player).filter(
                    Player.player_nickname == player_nickname
                ).update({"elo_rating": new_rating})

            # After calculating new ratings, store the prix results
            for player_nickname, placement in placements:
                player = db.query(Player).filter(Player.player_nickname == player_nickname).first()
                
                # Create or update prix result
                prix_result = (
                    db.query(PrixResult)
                    .filter(
                        PrixResult.prix_id == prix.prix_id,
                        PrixResult.player_id == player.player_id
                    )
                    .first()
                )
                
                if not prix_result:
                    prix_result = PrixResult(
                        prix_id=prix.prix_id,
                        player_id=player.player_id
                    )
                    db.add(prix_result)
                
                prix_result.placement = placement
                prix_result.starting_elo = current_ratings[player_nickname]
                prix_result.elo_adjustment = elo_adjustments[player_nickname]
                prix_result.ending_elo = new_ratings[player_nickname]
            
            db.commit()

            # Print results for this prix
            print(f"Prix {prix.prix_id} results:")
            for player_nickname, placement in placements:
                adjustment = elo_adjustments[player_nickname]
                new_rating = new_ratings[player_nickname]
                print(f"  {player_nickname}: {placement}th place, "
                      f"ELO {current_ratings[player_nickname]} → {new_rating} "
                      f"({'+'if adjustment > 0 else ''}{adjustment})")

        print("\nELO recalculation complete!")

def main():
    """Main function to run the ELO recalculation."""
    print("Starting ELO rating recalculation...")
    
    # Get all players from database
    with get_db_context() as db:
        players = db.query(Player.player_nickname).all()
        
    # Initialize ratings dict
    initial_ratings = {}
    
    # Get rating for each player from user input
    print("\nEnter initial ELO rating for each player:")
    for player in players:
        while True:
            try:
                rating = int(input(f"{player.player_nickname}: "))
                initial_ratings[player.player_nickname] = rating
                break
            except ValueError:
                print("Please enter a valid integer rating")
    
    # Confirm before proceeding
    response = input("This will reset all ELO ratings to custom values. Continue? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        return

    # Reset ratings to custom values
    reset_elo_ratings(initial_ratings)
    
    # Recalculate ratings
    recalculate_elo_ratings()

if __name__ == "__main__":
    main() 