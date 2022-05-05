import json
import os
from app.core import settings
from app.database.exceptions import DatabaseNotInitializedException, DatabaseAlreadyInitializedException
import app.models
from pymongo import MongoClient
import sys

"""Dummy Database """
class Database(object):
    def __init__(self):
        self.db=None
    
    def initialize(self):
        if os.path.isfile(settings.DATABASE_PATH) or self.db:
            raise DatabaseAlreadyInitializedException()
        with open(settings.DATABASE_PATH, "w") as db_handler: 
            self.db=dict()#{"router": {}, "switch": {}}
            for device_type in app.models.device_vendor_mapping.keys():
                self.db[device_type]=dict()
            json.dump(self.db, db_handler, indent=4)
        return True
    
    def read(self):
        if not os.path.isfile(settings.DATABASE_PATH):
            raise DatabaseNotInitializedException("Database seems to be uninitialized. Please run 'python3 -m app.initializer'")
        if self.db:
            return self.db
        with open(settings.DATABASE_PATH, "r") as db_handler:
            self.db=json.load(db_handler)
            return self.db
    
    def write(self):
        with open(settings.DATABASE_PATH, "w") as db_handler:
            json.dump(self.db, db_handler, indent=4)


"""Class connecting to database and implementing interfaces 
to communicate with it"""
class Mongo:
    def __init__(self):
        self.db=None
        
    """_summary_
    """
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

db=Mongo()