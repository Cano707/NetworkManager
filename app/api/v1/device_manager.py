from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv
from app.database import db as db_handler
import app.schemas
#from app.models import device_vendor_mapping
import app.models

device_router=APIRouter()

@cbv(device_router)
class DeviceCBV:
    """Represents API endpoints for the device manager."""
    db: dict = Depends(db_handler.read)
    
    @device_router.post("/{device_kind}/{key}")
    def add_device(self, key: str, device_kind: app.models.DeviceKinds, device: app.schemas.Device):
        """Add device to database

        Args:
            key (str): Specifies device
            device_kind (app.models.DeviceKinds): Supported device kinds
            device (schemas.Device): Represents device object

        Raises:
            Exception: Raised in case of an unknown error
            VendorModelNotSupportedException: Raised if vendor and/or model are not supported

        Returns:
            dict: {'detail': 'success'}
        """
        device=device.dict()
        vendor=device["vendor"]
        model=device["model"]
        # Check if vendor and/or model are supported
        print(vendor not in app.models.device_vendor_mapping[device_kind.value])
        print(model not in app.models.device_vendor_mapping[device_kind.value][vendor])
        if (vendor not in app.models.device_vendor_mapping[device_kind.value] or 
            model not in app.models.device_vendor_mapping[device_kind.value][vendor]):
                raise HTTPException(status_code=406, detail="VendorModelNotSupportedException")
        try:
            # Add device to database
            self.db[device_kind.value][key]=device
            db_handler.write()
            return {"detail": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail="Exception")
        
    @device_router.delete("/{device_kind}/{key}")
    def delete_device(self, key: str, device_kind: app.models.DeviceKinds) -> Dict[str, str]:
        """Deletes device specified by `key`

        Args:
            key (str): Specifies device
            device_kind (app.models.DeviceKinds): Supported device kinds

        Raises:
            Exception: Raised in case of an unknown error
            DeviceDoesNotExistException: Raised if device under `key` does not exist

        Returns:
            dict: {'detail': 'success'} if operation was successful 
        """
        if key not in self.db[device_kind.value]:
            raise HTTPException(status_code=406, detail="DeviceDoesNotExistException")
        try:
            self.db[device_kind.value].pop(key)
            return {"detail": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail="Exception")

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
        if key in self.db[device_kind.value]:
            raise HTTPException(status_code=406, detail="HostDoesNotExistException")
        try:
            for subkey, value in device.dict().items():
                # Update only those attributes of received device, if those are of type str.
                if type(value) is str:
                    self.db[device_kind.value][key][subkey]=value   
            db_handler.write()
            return {"detail": "success"}
        except Exception as e:
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
        if key in self.db[device_kind]:
            raise HTTPException(status_code=406, detail="DeviceDoesNotExistException")
        try:
            return self.db[device_kind.value][key]
        except Exception as e:
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
            return self.db[device_kind.value]
        except Exception as e:
            raise HTTPException(status_code=500, detail="Exception")
    
    
    
