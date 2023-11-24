from app.database import Connector
import app.models


class Initializer:
    
    def __init__(self):
        pass
    
    @staticmethod
    def initialize():
        db = Connector.connect()
        collections = db.list_collection_names()
        for device_type in app.models.device_vendor_mapping.keys():
            if device_type not in collections:
                db.create_collection(device_type)