from typing import List, NoReturn, Union
from app.database import db as db_handler
from app.crud.exceptions import InsertException, HostAlreadyExistsException


class CRUD:
    db = db_handler.get_instance()
    
    def __init__(self):
        pass
    
    
    """Creates an entry for a device

    Raises:
        HostAlreadyExistsException: Raised if the `key` already exists.
    """
    @classmethod
    def create(cls, key: str, device_type: str, device: dict): # device_type schemas.deviceTyüe
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
        
        
    """Reads and returns device with `key`

    Returns:
        Union[dict, None]: Returns dict with device data or None if device does not exist.
    """
    @classmethod
    def read(cls, key: str, device_type: str) -> Union[dict, None]:
        try:
            data=cls.db[device_type].find_one({"key": key})
        except Exception as e:
            #TODO - Logs
            raise
        return data
        
    """Reads and returns all devices of type `device_type`

    Returns:
        List[dict]: List of all devices as dicts
    """
    @classmethod
    def read_collection(cls, device_type: str) -> List[dict]:
        try:
            res=cls.db[device_type].find()
        except Exception as e:
            #TODO - Log
            raise
        res=list(res)
        return res
    

    """Updates an existing device"""
    @classmethod
    def update(cls, key: str, device_type: str, device: dict):
        update_device=dict()
        for field, value in device.items():
            if type(value) is dict:
                for sub_field, sub_value in value.items():
                    update_device[f"{field}.{sub_field}"]=sub_value
            else:
                update_device[field]=value  
        try:
            cls.db[device_type].update_one({"key": key}, {"$set": update_device})
        except Exception as e:
            #TODO - Logs
            print(e)
            raise
       
    """Deletes device with `key`

    Raises:
        e: General Exception
    """
    @classmethod
    def delete(cls, key: str, device_type: str):
        try:
            cls.db[device_type].delete_one({"key": key})
        except Exception as e:
            #TODO - Logs
            raise e
    