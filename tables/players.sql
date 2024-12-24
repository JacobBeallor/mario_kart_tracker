-- Create players table to store player information
CREATE TABLE players (
    player_id SERIAL PRIMARY KEY,
    player_first_name VARCHAR(50) NOT NULL,
    player_last_name VARCHAR(50) NOT NULL,
    player_nickname VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 