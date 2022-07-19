from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv
from app.database import db as db_handler
import app.schemas
#from app.models import device_vendor_mapping
import app.models
from app.crud import CRUD
from app.crud.exceptions import HostAlreadyExistsException
from app.core.autodetect import AutoDetector

device_router=APIRouter()

@cbv(device_router)
class DeviceCBV:
    """Represents API endpoints for the device manager."""
    #db: dict = Depends(db_handler.get_instance)
    
    @device_router.post("/{device_kind}/{key}")
    def add_device(self, key: str, device_kind: app.models.DeviceKinds, device: app.schemas.Device):
        """Add device to database

        **Args**:
        
            key (str): Specifies device
            device_kind (app.models.DeviceKinds): Supported device kinds
            device (schemas.Device): Represents device object

        **Device**:
        
            Opts: `model`, `vendor`, `ssh`, `telnet`, `serial`
            
        
        **Raises**:
        
            Error: Raised in case of an unknown error
            HostAlreadyExists: Raised when `key` already exists
            VendorModelNotSupported: Raised if vendor and/or model are not supported

        **Returns**:
        
            dict: {'detail': 'success'}
        """
        device=device.dict()
        vendor=device["vendor"]
        model=device["model"]
        if (device.autodetect):
            vendor, model = AutoDetector.run(device)
            pass
        elif (vendor != "" and model != "") and \
            (vendor not in app.models.device_vendor_mapping[device_kind.value] or 
             model not in app.models.device_vendor_mapping[device_kind.value][vendor]):
                raise HTTPException(status_code=406, detail="VendorModelNotSupported")
        try:
            CRUD.create(key, device_kind.value, device)
            return {"detail": "success"}
        except HostAlreadyExistsException as e:
            print(e)
            raise HTTPException(status_code=500, detail="HostAlreadyExists")
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Error")
        
    
        
        
    @device_router.delete("/{device_kind}/{key}")
    def delete_device(self, key: str, device_kind: app.models.DeviceKinds) -> Dict[str, str]:
        """Deletes device specified by `key`

        Args:
            key (str): Specifies device
            device_kind (app.models.DeviceKinds): Supported device kinds

        Raises:
            Exception: Raised in case of an unknown error

        Returns:
            dict: {'detail': 'success'} if operation was successful 
        """
        try:
            #self.db[device_kind.value].pop(key)
            CRUD.delete(key, device_kind.value)
            return {"detail": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail="Exception :See logs")

    @device_router.put("/{device_kind}/{key}")
    def update_device(self, key: str, device_kind: app.models.DeviceKinds, device: app.schemas.DeviceUpdate):
        """Updates device attributes of device specified by `key`

        Args:
            key (str): Specifies device
            device_kind (app.models.DeviceKinds): Supported device kinds
            device (schemas.DeviceUpdate): Represents device object

        Raises:
            Exception: Raised in case of an unknown error
            HostDoesNotExistException: Raised if device under `key` does not exist

        Returns:
            dict: {'detail': 'success'} if operation was successful 
        """
        #if key in self.db[device_kind.value]:
        #    raise HTTPException(status_code=406, detail="HostDoesNotExistException")
        update_device=dict()
        try:
            for device_key, value in device.dict().items():
                # Update only those attributes of received device, if those are of type str.
                if type(value) is str and value:
                    #self.db[device_kind.value][key][subkey]=value   
                    update_device[device_key]=value
                elif type(value) is dict:
                    update_device[device_key]=dict()
                    for subkey, subvalue in value.items():
                        if type(subvalue) is str and subvalue:
                            update_device[device_key][subkey]=subvalue
            #db_handler.write()
            CRUD.update(key, device_kind.value, update_device)
            return {"detail": "success"}
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Exception")
 
        
    @device_router.get("/{device_kind}/{key}")
    def get_device(self, key: str, device_kind: app.models.DeviceKinds):
        """Returns device of type `device_kind` specified by `key`

        Args:
            key (str): Specifies device
            device_kind (app.models.DeviceKinds): Supported device kinds

        Raises:
            Exception: Raised in case of an unknown error
            DeviceDoesNotExistException: Raised if device under `key` does not exist

        Returns:
            dict: Specified device
        """
        #if key in self.db[device_kind]:
        #    raise HTTPException(status_code=406, detail="DeviceDoesNotExistException")
        try:
            #return self.db[device_kind.value][key]
            
            data=CRUD.read(key, device_kind.value)
            data.pop("_id")
            return data
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Exception")
    
    @device_router.get("/{device_kind}")
    def get_all_devices(self, device_kind: app.models.DeviceKinds):
        """Returns all devices of type `device_kind`

        Args:
            device_kind (app.models.DeviceKinds): Supported device kinds

        Raises:
            Exception: Raised in case of an unknown error

        Returns:
            dict: All stored devices of `device_kind`
        """
        try:
            #return self.db[device_kind.value]
            data=CRUD.read_collection(device_kind.value)
            for device in data:
                device.pop("_id")
            return data
        except Exception as e:
            raise HTTPException(status_code=500, detail="Exception")
    
    
    
