from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from fastapi_utils.cbv import cbv
from zmq import device
from app.database import db as db_handler
from app import schemas
from app.models import device_vendor_mapping

device_router=APIRouter()

@cbv(device_router)
class DeviceCBV:
    db: dict = Depends(db_handler.read)
    
    @device_router.post("/{device_kind}/add/{hostname}")
    def add_device(self, hostname: str, device_kind: schemas.DeviceKinds, device: schemas.Device):
        try:
            self.db[device_kind.value][hostname]=device.dict()
            db_handler.write()
            return {"message": "success"}
        except Exception as e:
            return {"Exception": "Internal Server Error"}

    @device_router.put("/{device_kind}/update/{hostname}")
    def update_device(self, hostname: str, device_kind: schemas.DeviceKinds, device: schemas.DeviceUpdate):
        try:
            if not hostname in self.db[device_kind.value]:
                return {"message": "Host {hostname} does not exist."}
            self.db[device_kind.value][hostname].update(device.dict())    
            db_handler.write()
            return {"message": "success"}
        except Exception as e:
            return {"Exception": "Internal Server Error"}
        
    @device_router.get("/{device_kind}/get/{hostname}")
    def get_device(self, device_kind: schemas.DeviceKinds, hostname: str):
        if hostname in self.db[device_kind]:
            return self.db[device_kind.value][hostname]
        return {"Error": f"Host {hostname} does not exist."}
    
    @device_router.get("/{device_kind}/get-all")
    def get_all_devices(self, device_kind: schemas.DeviceKinds):
        return self.db[device_kind.value]
    
    @device_router.get("/{device_kind}/info/vendors")
    def supported_vendors(self, device_kind: schemas.DeviceKinds):
        vendor_model_mapping=device_vendor_mapping[device_kind.value]
        vendors=list(vendor_model_mapping.keys())
        return {"vendors": vendors}
    
    @device_router.get("/{device_kind}/info/{vendor}")
    def supported_vendor_models(self, device_kind: schemas.DeviceKinds, vendor: schemas.Vendors):
        pass