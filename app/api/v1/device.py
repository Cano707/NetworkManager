from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from fastapi_utils.cbv import cbv
from zmq import device
from app.database import db as db_handler
from app import schemas

device_router=APIRouter()

@cbv(device_router)
class DeviceCBV:
    db: dict = Depends(db_handler.read)
    
    @device_router.post("/{device_kind}/add")
    def add_device(self, device_kind: schemas.DeviceKinds, device: schemas.Device):
        try:
            self.db[device_kind.value][device.hostname]=device.dict()
            db_handler.write()
            return {"message": "success"}
        except Exception as e:
            return {"Exception": "Internal Server Error"}
        
    @device_router.put("/{device_kind}/update")
    def update_device(self, device_kind: schemas.DeviceKinds, device: schemas.Device):
        try:
            self.db[device_kind.value][device.hostname]=device.dict()
            db_handler.write()
            return {"message": "success"}
        except Exception as e:
            return {"Exception": "Internal Server Error"}
        
    @device_router.get("/{device_kind}/get/{hostname}")
    def get_device(self, device_kind: schemas.DeviceKinds, hostname: str):
        if hostname in self.db[device_kind]:
            return self.db[device_kind.value][hostname]
        return {"Error": f"Host {hostname} does not exist."}

    @device_router.get("/{device_kind}/get")
    def get_devices(self, device_kind: str, hostnames: Optional[List[str]] = Query(None)):
        result=dict()
        for hostname in hostnames:
            if hostname in self.db[device_kind]:
                result[hostname]=self.db[device_kind][hostname]
        return result
    
    @device_router.get("/{device_kind}/get-all")
    def get_all_devices(self, device_kind: str):
        return self.db[device_kind]
    
