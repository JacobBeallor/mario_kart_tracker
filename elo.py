from typing import List, Dict, Tuple
import math


def calculate_elo_adjustments(
    placements: List[Tuple[str, int]],  # List of (player_name, finish_position) tuples
    current_ratings: Dict[str, int],     # Dict of player_name: current_elo_rating
    k_factor: int = 32,                  # How volatile the ratings are (higher = more movement)
) -> Dict[str, int]:
    """
    Calculate ELO rating adjustments for a Mario Kart prix.
    
    Args:
        placements: List of tuples containing (player_name, finish_position)
        current_ratings: Dictionary of current ELO ratings for each player
        k_factor: How much ratings can change (default: 32)
    
    Returns:
        Dictionary of ELO rating changes for each player
    
    Example:
        placements = [("Alice", 1), ("Bob", 2), ("Charlie", 3)]
        current_ratings = {"Alice": 1500, "Bob": 1600, "Charlie": 1400}
        adjustments = calculate_elo_adjustments(placements, current_ratings)
        # Returns something like: {"Alice": 15, "Bob": -5, "Charlie": -10}
    """
    num_players = len(placements)
    adjustments = {name: 0 for name, _ in placements}
    
    # Calculate adjustments for each pair of players
    for i in range(num_players):
        player1, pos1 = placements[i]
        rating1 = current_ratings[player1]
        
        for j in range(i + 1, num_players):
            player2, pos2 = placements[j]
            rating2 = current_ratings[player2]
            
            # Calculate expected scores
            rating_diff = (rating2 - rating1) / 400.0
            expected1 = 1 / (1 + math.pow(10, rating_diff))
            expected2 = 1 - expected1
            
            # Calculate actual scores (1 for win, 0.5 for tie, 0 for loss)
            actual1 = 1.0 if pos1 < pos2 else 0.0 if pos1 > pos2 else 0.5
            actual2 = 1.0 - actual1
            
            # Calculate and accumulate adjustments
            adj1 = k_factor * (actual1 - expected1)
            adj2 = k_factor * (actual2 - expected2)
            
            adjustments[player1] += adj1
            adjustments[player2] += adj2
    
    # Convert floating point adjustments to integers
    return {
        player: round(adjustment / (num_players - 1))
        for player, adjustment in adjustments.items()
    }

def apply_elo_adjustments(
    current_ratings: Dict[str, int],
    adjustments: Dict[str, int],
    min_rating: int = 0
) -> Dict[str, int]:
    """
    Apply ELO adjustments to current ratings, ensuring no rating goes below min_rating.
    
    Args:
        current_ratings: Dictionary of current ELO ratings
        adjustments: Dictionary of ELO adjustments to apply
        min_rating: Minimum allowed rating (default: 0)
    
    Returns:
        Dictionary of new ELO ratings
    """
    return {
        player: max(min_rating, current_ratings[player] + adjustment)
        for player, adjustment in adjustments.items()
    }