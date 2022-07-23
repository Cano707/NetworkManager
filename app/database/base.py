from app.core import settings
from app.database.exceptions import DatabaseNotInitializedException, DatabaseAlreadyInitializedException
import app.models
from pymongo import MongoClient
import sys


class Connection:    
    """
    Class interface offering methods to connect to MongoDB
    """
    
    def __init__(self):
        self.db=None
        
    def initialize(self):
        if self.db:
            return self.db
        try:
            client=MongoClient(settings.DATABASE_URL, username=settings.USERNAME, password=settings.PASSWORD, authSource=settings.AUTH_DATABASE)
            self.db=client.networkmanager
            collections=self.db.list_collection_names()
            for device_type in app.models.device_vendor_mapping.keys():
                if device_type not in collections:
                    self.db.create_collection(device_type)
        except ConnectionError as e:
            #TODO - Logging
            print(e)
            sys.exit(1)
        except Exception as e:
            #TODO - Logging
            print(e)
            sys.exit(1)
            
    def get_instance(self):
        if self.db is not None:
            return self.db
        else:
            self.initialize()
            return self.db
