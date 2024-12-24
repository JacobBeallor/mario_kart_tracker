-- Create prixs table to store grand prix information
CREATE TABLE prixs (
    prix_id SERIAL PRIMARY KEY,
    prix_type VARCHAR(10) NOT NULL CHECK (prix_type IN ('grand_prix', 'vs_race')),
    cup_name VARCHAR(50),
    number_of_players INTEGER NOT NULL CHECK (number_of_players IN (1, 2, 3, 4)),
    cc_class INTEGER NOT NULL CHECK (cc_class IN (50, 100, 150, 200)),
    is_mirror_mode BOOLEAN DEFAULT FALSE,
    is_teams_mode BOOLEAN DEFAULT FALSE,
    items_setting VARCHAR(10) NOT NULL CHECK (items_setting IN ('normal', 'shells_only', 'bananas_only', 'mushrooms_only', 'bob-ombs_only', 'coins_only', 'frantic_items', 'customer_items', 'none')),
    com_level VARCHAR(10) NOT NULL CHECK (com_level IN ('normal', 'hard')),
    com_vehicles VARCHAR(10) NOT NULL CHECK (com_vehicles IN ('all', 'bikes_only', 'karts_only')),
    courses_setting VARCHAR(10) NOT NULL CHECK (courses_setting IN ('choose', 'random', 'in_order')),
    race_count INTEGER NOT NULL CHECK (race_count IN (4, 6, 8, 12, 16, 24, 32, 48)),
    date_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
); 