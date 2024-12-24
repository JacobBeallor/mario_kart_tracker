from dataclasses import dataclass
from os import environ

@dataclass
class DatabaseConfig:
    username: str = environ.get('DB_USERNAME', 'postgres')
    password: str = environ.get('DB_PASSWORD', 'postgres')
    host: str = environ.get('DB_HOST', 'localhost')
    port: str = environ.get('DB_PORT', '5432')
    database: str = environ.get('DB_NAME', 'mario_kart')

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

config = DatabaseConfig() 