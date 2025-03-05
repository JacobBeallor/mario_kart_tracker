-- Create prix_results table to store prix placements and ELO changes
CREATE TABLE prix_results (
    result_id SERIAL PRIMARY KEY,
    prix_id INTEGER REFERENCES prixs(prix_id),
    player_id INTEGER REFERENCES players(player_id),
    placement INTEGER NOT NULL CHECK (placement > 0),
    starting_elo INTEGER NOT NULL,
    elo_adjustment INTEGER NOT NULL,
    ending_elo INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(prix_id, player_id)
); 