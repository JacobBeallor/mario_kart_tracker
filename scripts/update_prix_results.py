from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now you can import from models.py
from models import Prix, Race, RaceResult, Player, PrixResult
from collections import defaultdict


# You'll need to adjust this connection string based on your database configuration
DATABASE_URL = "postgresql://postgres:Solomon%%2312@localhost/mario_kart"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def calculate_elo_change(rating_a, rating_b, actual_score, k_factor=32):
    """Calculate ELO rating change."""
    expected_score = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    return round(k_factor * (actual_score - expected_score))

def populate_prix_results():
    session = Session()
    
    try:
        # Get all prix events that don't have results yet
        prix_without_results = session.query(Prix).outerjoin(PrixResult).filter(PrixResult.prix_id == None).all()
        
        for prix in prix_without_results:
            print(f"Processing prix_id: {prix.prix_id}")
            
            # Get all race results for this prix
            race_results = (
                session.query(RaceResult)
                .join(Race)
                .filter(Race.prix_id == prix.prix_id)
                .all()
            )
            
            # Calculate total points per player
            player_points = defaultdict(int)
            for result in race_results:
                player_points[result.player_id] += result.points_earned
            
            # Sort players by points to determine placement
            sorted_players = sorted(
                player_points.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Get player ELO ratings at the time
            player_ratings = {}
            for player_id, _ in sorted_players:
                player = session.query(Player).filter_by(player_id=player_id).first()
                player_ratings[player_id] = player.elo_rating
            
            # Calculate ELO adjustments
            num_players = len(sorted_players)
            for i, (player_id, points) in enumerate(sorted_players):
                placement = i + 1
                starting_elo = player_ratings[player_id]
                
                # Calculate ELO adjustment based on head-to-head results with every other player
                total_elo_change = 0
                for j, (opponent_id, _) in enumerate(sorted_players):
                    if opponent_id != player_id:
                        # Winner gets 1, loser gets 0
                        actual_score = 1 if i < j else 0
                        if i == j:
                            actual_score = 0.5
                        
                        elo_change = calculate_elo_change(
                            starting_elo,
                            player_ratings[opponent_id],
                            actual_score,
                            k_factor=32//(num_players-1)  # Adjust k-factor based on number of players
                        )
                        total_elo_change += elo_change
                
                # Create prix result entry
                prix_result = PrixResult(
                    prix_id=prix.prix_id,
                    player_id=player_id,
                    placement=placement,
                    starting_elo=starting_elo,
                    elo_adjustment=total_elo_change,
                    ending_elo=starting_elo + total_elo_change
                )
                session.add(prix_result)
                
                # Update player's ELO rating
                player = session.query(Player).filter_by(player_id=player_id).first()
                player.elo_rating = starting_elo + total_elo_change
            
            session.commit()
            print(f"Completed processing prix_id: {prix.prix_id}")
            
    except Exception as e:
        session.rollback()
        print(f"Error: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    populate_prix_results() 