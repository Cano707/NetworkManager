from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "NetworkManager"
    DATABASE_PATH: str = os.path.abspath(os.path.join("app", "database.json"))
    
settings=Settings()