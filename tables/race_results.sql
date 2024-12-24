-- Create race_results table to store race results for each player
CREATE TABLE race_results (
    result_id SERIAL PRIMARY KEY,
    race_id INTEGER REFERENCES races(race_id),
    player_id INTEGER REFERENCES players(player_id),
    combo_id INTEGER REFERENCES kart_combos(combo_id),
    finish_position INTEGER NOT NULL CHECK (finish_position BETWEEN 1 AND 12),
    points_earned INTEGER NOT NULL CHECK (points_earned BETWEEN 1 AND 15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(race_id, player_id),
    UNIQUE(race_id, finish_position)
); 