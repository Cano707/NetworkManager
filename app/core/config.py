from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "NetworkManager"
    #DATABASE_PATH: str = os.path.abspath(os.path.join("app", "database.json"))
    DATABASE_URL: str = "127.0.0.1"
    USERNAME: str = "cano"
    PASSWORD: str = "1234"
    DATABASE: str = "networkmanager"
    AUTH_DATABASE: str = "networkmanager"
    
settings=Settings()