from typing import List, Union
#from app.database import db as db_handler
from app.database import Connector
from app.crud.exceptions import HostAlreadyExistsException


class CRUD:
    #db = db_handler.get_instance()
    db = Connector.connect()
    
    def __init__(self):
        pass
    
    @classmethod
    def create(cls, key: str, device_type: str, device: dict): # device_type schemas.deviceTyüe
        """Creates an entry for a device

        Raises:
            HostAlreadyExistsException: Raised if the `key` already exists.
        """
        data={"key":key, **device}
        try:
            res=cls.db[device_type].update_one({"key": key}, {"$setOnInsert": data}, upsert=True)
        except Exception as e:
            #TODO - Log
            print(e)
            raise 
        if "upserted" not in res.raw_result:
            #TODO - Log: Already exists
            raise HostAlreadyExistsException()
        
        
    @classmethod
    def read(cls, key: str, device_type: str) -> Union[dict, None]:
        """Reads and returns device with `key`

        Returns:
            Union[dict, None]: Returns dict with device data or None if device does not exist.
        """
        print(f"[i] CRUD - read: {key=}\t{device_type=}")
        try:
            data=cls.db[device_type].find_one({"key": key}, {'_id': 0})
        except Exception as e:
            #TODO - Logs
            raise
        return data
        
    @classmethod
    def read_collection(cls, device_type: str) -> List[dict]:
        """Reads and returns a collection

        Returns:
            Union[dict, None]: Returns a list with the collection
        """
        try:
            res=cls.db[device_type].find()
        except Exception as e:
            #TODO - Log
            raise
        res=list(res)
        return res
    

    
    @classmethod
    def update(cls, key: str, device_type: str, device: dict): # -> Noreturn
        """Updates an existing device

        Returns:
            --
        """
        """
        update_device=dict()
        for field, value in device.items():
            if type(value) is dict:
                for sub_field, sub_value in value.items():
                    update_device[f"{field}.{sub_field}"]=sub_value
            else:
                update_device[field]=value  
        """
        try:
            #cls.db[device_type].update_one({"key": key}, {"$set": update_device})
            cls.db[device_type].update_one({"key": key}, {"$set": device})
        except Exception as e:
            #TODO - Logs
            print(f"{key=}")
            print(f"{device_type=}")
            print(f"{device=}")
            print(e)
            raise
       
    
    @classmethod
    def delete(cls, key: str, device_type: str):
        """Deletes device with `key`

        Raises:
            e: General Exception
        """
        try:
            cls.db[device_type].delete_one({"key": key})
        except Exception as e:
            #TODO - Logs
            raise e
    