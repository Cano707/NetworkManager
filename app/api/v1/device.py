from typing import Dict, List
from fastapi import APIRouter, Depends, Query
from fastapi_utils.cbv import cbv
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
        
    
    
    @device_router.post("/router/add/{hostname}")
    def add_router(self, hostname: str, device: schemas.Device):
        try:
            self.db["router"][hostname]=device.dict()
            db_handler.write()
        except Exception as e:
            return {"Error": "Internal Server Error"}
        return {"message": "success"}
        
    @device_router.put("/router/update/{hostname}")
    def update_router(self, hostname: str, device: schemas.DeviceUpdate):
        self.db["router"][hostname].update(device.dict())
        db_handler.write()
        return {"message": "success"}
        
    @device_router.get("/router/get/{hostname}", response_model=schemas.DeviceResponse)
    def get_router(self, hostname: str):
        return self.db["router"][hostname]
    
    @device_router.get("/router/get", response_model=Dict[str, schemas.DeviceResponse])
    def get_routers(self, hostnames: List[str] = Query(None)):
        response=dict()
        for hostname in hostnames:
            response[hostname]=self.db["router"][hostname]
        return response
    
    @device_router.get("/router", response_model=Dict[str, schemas.DeviceResponse]) 
    def get_all_routers(self):
        return self.db["router"]
    
    @device_router.post("/switch/add/{hostname}")
    def add_switch(self, hostname: str, device: schemas.Device):
        try:
            self.db["switch"][hostname]=device.dict()
            db_handler.write()
        except Exception as e:
            return {"Error": "Internal Server Error"}
        return {"message": "success"}
    
    @device_router.put("/switch/update/{hostname}")
    def update_switch(self, hostname: str, device: schemas.DeviceUpdate):
        self.db["switch"][hostname].update(device.dict())
        db_handler.write()
        return {"message": "success"}
    
    @device_router.get("/switch/get/{hostname}", response_model=schemas.DeviceResponse)
    def get_switch(self, hostname: str):
        return self.db["switch"][hostname]
    
    @device_router.get("/switch/get", response_model=Dict[str, schemas.DeviceResponse])
    def get_switches(self, hostnames: List[str] = Query(None)):
        response=dict()
        for hostname in hostnames:
            response[hostname]=self.db["switch"][hostname]
        return response
    
    @device_router.get("/switch", response_model=Dict[str, schemas.DeviceResponse])
    def get_all_switches(self):
        return self.db["switch"]
    
