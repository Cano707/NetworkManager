from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv
from zmq import device
from app.database import db as db_handler
from app import schemas
#from app.models import device_vendor_mapping
import app.models

device_router=APIRouter()

#TODO - Refactoring
#TODO - Plastic surgery
#TODO - Exception handling
@cbv(device_router)
class DeviceCBV:
    db: dict = Depends(db_handler.read)
    
    @device_router.post("/{device_kind}/{key}")
    def add_device(self, key: str, device_kind: app.models.DeviceKinds, device: schemas.Device):
        try:
            #TODO - Check if vendor and model are supported
            self.db[device_kind.value][key]=device.dict()
            db_handler.write()
            return {"message": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail="error, see logs.")

    @device_router.put("/{device_kind}/{key}")
    def update_device(self, key: str, device_kind: app.models.DeviceKinds, device: schemas.DeviceUpdate):
        try:
            if not key in self.db[device_kind.value]:
                return {"message": "Host {hostname} does not exist."}
            for subkey, value in device.dict().items():
                if type(value) is str:
                    self.db[device_kind.value][key][subkey]=value   
            db_handler.write()
            return {"message": "success"}
        except Exception as e:
            return {"Exception": "Internal Server Error"}
        
    @device_router.get("/{device_kind}/{key}/get")
    def get_device(self, device_kind: app.models.DeviceKinds, key: str):
        if key in self.db[device_kind]:
            return self.db[device_kind.value][key]
        return {"Error": f"Host {key} does not exist."}
    
    @device_router.get("/{device_kind}/get-all")
    def get_all_devices(self, device_kind: app.models.DeviceKinds):
        return self.db[device_kind.value]
    
    
    
