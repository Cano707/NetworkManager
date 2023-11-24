from app.core import Settings
from app.database.exceptions import DatabaseNotInitializedException, DatabaseAlreadyInitializedException
import app.models
from pymongo import MongoClient
import sys


class Connector:    
    """
    Class interface offering methods to connect to MongoDB
    """
    
    def __init__(self):
        pass 
        
    @staticmethod
    def connect():
        try:
            # Authentication is not yet enabled in /etc/mongod.conf
            client=MongoClient(Settings.DATABASE_URL)#, username=settings.USERNAME, password=settings.PASSWORD, authSource=settings.AUTH_DATABASE)
            db=client.networkmanager
            return db
        except ConnectionError as e:
            #TODO - Logging
            print(e)
            sys.exit(1)
        except Exception as e:
            #TODO - Logging
            print(e)
            sys.exit(1)
        
