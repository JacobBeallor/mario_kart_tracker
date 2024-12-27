from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Prix(Base):
    __tablename__ = 'prixs'

    prix_id = Column(Integer, primary_key=True)
    prix_type = Column(String(10), CheckConstraint("prix_type IN ('grand_prix', 'vs_race')"), nullable=False)
    cup_name = Column(String(50))
    number_of_players = Column(Integer, CheckConstraint("number_of_players IN (1, 2, 3, 4)"), nullable=False)
    cc_class = Column(Integer, CheckConstraint("cc_class IN (50, 100, 150, 200)"), nullable=False)
    is_mirror_mode = Column(Boolean, default=False)
    is_teams_mode = Column(Boolean, default=False)
    items_setting = Column(
        String(10), 
        CheckConstraint("items_setting IN ('normal', 'shells_only', 'bananas_only', 'mushrooms_only', 'bob-ombs_only', 'coins_only', 'frantic_items', 'customer_items', 'none')"),
        nullable=False
    )
    com_level = Column(String(10), CheckConstraint("com_level IN ('normal', 'hard')"), nullable=False)
    com_vehicles = Column(String(10), CheckConstraint("com_vehicles IN ('all', 'bikes_only', 'karts_only')"), nullable=False)
    courses_setting = Column(String(10), CheckConstraint("courses_setting IN ('choose', 'random', 'in_order')"), nullable=False)
    race_count = Column(Integer, CheckConstraint("race_count IN (4, 6, 8, 12, 16, 24, 32, 48)"), nullable=False)
    date_played = Column(DateTime, default=datetime.utcnow)

    races = relationship("Race", back_populates="prix")

class Player(Base):
    __tablename__ = 'players'

    player_id = Column(Integer, primary_key=True)
    player_first_name = Column(String(50), nullable=False)
    player_last_name = Column(String(50), nullable=False)
    player_nickname = Column(String(50), nullable=False)
    elo_rating = Column(Integer, nullable=False, default=1500)
    created_at = Column(DateTime, default=datetime.utcnow)

    race_results = relationship("RaceResult", back_populates="player")

class KartCombo(Base):
    __tablename__ = 'kart_combos'

    combo_id = Column(Integer, primary_key=True)
    character_name = Column(String(50), nullable=False)
    vehicle_name = Column(String(50), nullable=False)
    tire_name = Column(String(50), nullable=False)
    glider_name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    race_results = relationship("RaceResult", back_populates="kart_combo")

class Track(Base):
    __tablename__ = 'tracks'

    track_id = Column(Integer, primary_key=True)
    track_name = Column(String(100), nullable=False, unique=True)
    cup_name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    races = relationship("Race", back_populates="track")

class Race(Base):
    __tablename__ = 'races'

    race_id = Column(Integer, primary_key=True)
    prix_id = Column(Integer, ForeignKey('prixs.prix_id'))
    track_id = Column(Integer, ForeignKey('tracks.track_id'))
    race_number = Column(Integer, CheckConstraint("race_number > 0"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    prix = relationship("Prix", back_populates="races")
    track = relationship("Track", back_populates="races")
    race_results = relationship("RaceResult", back_populates="race")

    __table_args__ = (
        CheckConstraint('race_number > 0'),
    )

class RaceResult(Base):
    __tablename__ = 'race_results'

    result_id = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey('races.race_id'))
    player_id = Column(Integer, ForeignKey('players.player_id'))
    combo_id = Column(Integer, ForeignKey('kart_combos.combo_id'))
    finish_position = Column(Integer, CheckConstraint("finish_position BETWEEN 1 AND 12"), nullable=False)
    points_earned = Column(Integer, CheckConstraint("points_earned BETWEEN 1 AND 15"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    race = relationship("Race", back_populates="race_results")
    player = relationship("Player", back_populates="race_results")
    kart_combo = relationship("KartCombo", back_populates="race_results")

    __table_args__ = (
        CheckConstraint('finish_position BETWEEN 1 AND 12'),
        CheckConstraint('points_earned BETWEEN 1 AND 15'),
    )