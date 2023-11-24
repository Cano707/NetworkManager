import os

"""Global configurations"""
class Settings:
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "NetworkManager"
    #DATABASE_PATH: str = os.path.abspath(os.path.join("app", "database.json"))
    DATABASE_URL: str = "127.0.0.1"
    #USERNAME: str = "cano" #TODO Is replaced with env var $USER and $USERNAME - THE GIVEN VALUE IS NOT USED BUT REPLACED
    #PASSWORD: str = "4321"
    DATABASE: str = "networkmanager"
    AUTH_DATABASE: str = "networkmanager"
    DEVICE_LOG_PATH: str = os.path.join("./", "app", "device_logs")
    APP_LOG_PATH: str = os.path.join("./", "app", "logs")
    LOG_LEVEL: str = 10 
    