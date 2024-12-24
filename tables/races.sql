-- Create races table to store individual race information
CREATE TABLE races (
    race_id SERIAL PRIMARY KEY,
    prix_id INTEGER REFERENCES prixs(prix_id),
    track_id INTEGER REFERENCES tracks(track_id),
    race_number INTEGER NOT NULL CHECK (race_number > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(prix_id, race_number)
); 