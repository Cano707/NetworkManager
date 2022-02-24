import json
import os
from app.core import settings
from app.database.exceptions import DatabaseNotInitializedException, DatabaseAlreadyInitializedException


class Database(object):
    def __init__(self):
        self.db=None
    
    def initialize(self):
        if os.path.isfile(settings.DATABASE_PATH) or self.db:
            raise DatabaseAlreadyInitializedException()
        with open(settings.DATABASE_PATH, "w") as db_handler: 
            self.db={"router": {}, "switch": {}}
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

    
db=Database()