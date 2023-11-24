from typing import Dict
from fastapi import APIRouter, HTTPException
from fastapi_utils.cbv import cbv
import app.schemas
import app.models
from app.crud import CRUD
from app.crud.exceptions import HostAlreadyExistsException
from app.core.autodetect import AutoDetector
from app.core.exceptions import MissingConnectionData, ConnectionError, NoSuchDeviceException
from app.core.connector import Connector
from app.core.device_backend import Device


device_router=APIRouter()

@cbv(device_router)
class DeviceAPI:
    """Represents API endpoints for the device manager."""
    
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
        try:
            return Device.add_device(key=key, device_kind=device_kind, device=device)
        except:
            raise 
        
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
            return Device.delete_device(key=key, device_kind=device_kind)
        except:
            raise
        
    @device_router.post("/{device_kind}/{key}/reload")
    def reload_device(cls, key: str, device_kind: app.models.DeviceKinds, vendor: str, model: str):
        try:
            return Device.reload_device(key=key, device_kind=device_kind, vendor=vendor, model=model)
        except:
            raise

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
        try:
            return Device.update_device(key=key, device_kind=device_kind, device=device)
        except:
            raise
        
 
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
        try:
            return Device.get_device(key=key, device_kind=device_kind)
        except:
            raise
    
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
            return Device.get_all_devices(device_kind=device_kind)
        except:
            raise
