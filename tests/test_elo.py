import pytest
from elo import calculate_elo_adjustments, apply_elo_adjustments, get_rating_change_description

def test_basic_elo_calculation():
    # Test basic scenario with 3 players
    placements = [
        ("Alice", 1),  # Winner
        ("Bob", 2),    # Second
        ("Charlie", 3) # Third
    ]
    
    current_ratings = {
        "Alice": 1500,
        "Bob": 1500,
        "Charlie": 1500
    }
    
    adjustments = calculate_elo_adjustments(placements, current_ratings)
    
    # Winner should gain points, loser should lose points
    assert adjustments["Alice"] > 0
    assert adjustments["Charlie"] < 0
    # Sum of adjustments should be close to zero
    assert abs(sum(adjustments.values())) <= 1

def test_upset_victory():
    # Test when a lower-rated player beats higher-rated players
    placements = [
        ("Underdog", 1),     # 1200 rated player wins
        ("Favorite", 2),     # 1800 rated player second
        ("MidPlayer", 3)     # 1500 rated player third
    ]
    
    current_ratings = {
        "Underdog": 1200,
        "Favorite": 1800,
        "MidPlayer": 1500
    }
    
    adjustments = calculate_elo_adjustments(placements, current_ratings)
    
    # Underdog should gain more points than in a normal victory
    assert adjustments["Underdog"] > 20
    # Favorite should lose more points than in a normal loss
    assert adjustments["Favorite"] < -10

def test_expected_outcome():
    # Test when players finish exactly as their ratings would predict
    placements = [
        ("High", 1),    # Highest rated wins
        ("Mid", 2),     # Middle rated second
        ("Low", 3)      # Lowest rated third
    ]
    
    current_ratings = {
        "High": 1800,
        "Mid": 1500,
        "Low": 1200
    }
    
    adjustments = calculate_elo_adjustments(placements, current_ratings)
    
    # Changes should be relatively small
    assert abs(adjustments["High"]) < 10
    assert abs(adjustments["Mid"]) < 10
    assert abs(adjustments["Low"]) < 10

def test_apply_adjustments():
    current_ratings = {"Player1": 1500, "Player2": 1400}
    adjustments = {"Player1": -20, "Player2": 15}
    
    new_ratings = apply_elo_adjustments(current_ratings, adjustments)
    
    assert new_ratings["Player1"] == 1480
    assert new_ratings["Player2"] == 1415

def test_minimum_rating():
    current_ratings = {"Player1": 50, "Player2": 1400}
    adjustments = {"Player1": -100, "Player2": 15}
    
    new_ratings = apply_elo_adjustments(
        current_ratings, 
        adjustments,
        min_rating=0
    )
    
    assert new_ratings["Player1"] == 0  # Should not go below minimum
    assert new_ratings["Player2"] == 1415

def test_rating_change_description():
    assert get_rating_change_description(15) == "+15"
    assert get_rating_change_description(-10) == "-10"
    assert get_rating_change_description(0) == "0"

def test_large_field():
    # Test with more players
    placements = [
        ("P1", 1), ("P2", 2), ("P3", 3), ("P4", 4),
        ("P5", 5), ("P6", 6), ("P7", 7), ("P8", 8)
    ]
    
    current_ratings = {
        f"P{i}": 1500 for i in range(1, 9)
    }
    
    adjustments = calculate_elo_adjustments(placements, current_ratings)
    
    # Verify basic properties
    assert len(adjustments) == 8
    assert adjustments["P1"] > adjustments["P8"]
    assert abs(sum(adjustments.values())) <= 1

if __name__ == "__main__":
    pytest.main([__file__]) 