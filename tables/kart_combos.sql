-- Create kart_combos table to store different kart configurations
CREATE TABLE kart_combos (
    combo_id SERIAL PRIMARY KEY,
    character_name VARCHAR(50) NOT NULL,
    vehicle_name VARCHAR(50) NOT NULL,
    tire_name VARCHAR(50) NOT NULL,
    glider_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 