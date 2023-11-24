from typing import Dict
from fastapi import APIRouter, HTTPException
from fastapi_utils.cbv import cbv
import app.schemas
import app.models
from app.crud import CRUD
from app.crud.exceptions import HostAlreadyExistsException
from app.core.autodetect import AutoDetector
from app.core.exceptions import MissingConnectionData, ConnectionError, NoSuchDeviceException, NoConnectionPossibleException
from app.core.connector import Connector
from app.core.connect_backend import Connect
import traceback

class Device:
    """Represents API endpoints for the device manager."""
    
    @classmethod
    def add_device(cls, key: str, device_kind: app.models.DeviceKinds, device: app.schemas.Device):
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
        print("[i] add_device: RUNNING")
        device=device.dict()
        if "vendor" in device and "model" in device:
            vendor=device["vendor"]
            model=device["model"]
        elif not device["autodetect"]:
            raise HTTPException(status_code = 406, detail = "InvalidData")
            
        
        
        # Check if autodetection is wanted. If not, check if vendor and model have been given and raise an exception accordingly.
        if device["autodetect"]:
            print("[i] add_device: DETECTING DEVICE")
            try:
                vendor, model, guess = AutoDetector.run(key, device, device_kind)
            except MissingConnectionData as e:
                raise HTTPException(status_code=406, detail="MissingConnectionData")
            except ConnectionError as e:
                raise HTTPException(status_code=406, detail="ConnectionError")
            
            device["vendor"] = vendor
            device["model"] = model
            if guess:
                if "ssh" in device and "device_type" in device["ssh"]:
                    device["ssh"]["device_type"] = guess
                if "telnet" in device and "device_type" in device["ssh"]:
                    device["telnet"]["device_type"] = guess
                
        elif (vendor not in app.models.device_vendor_mapping[device_kind.value] or model not in app.models.device_vendor_mapping[device_kind.value][vendor]):
                raise HTTPException(status_code=406, detail="VendorModelNotSupported")
            
        # Drop field(s) which are not meant be written into the database. 
        device.pop("autodetect", None)
        initial_read = device.pop("initial_read", None)
        
        try:
            CRUD.create(key, device_kind.value, device)
            print("[i] add_device: DEVICE CREATED")
            
            #TODO Initial reading - Is meant to be somewhere else but fuck it
            
            connection_data = device["ssh"]
            connection_data["secret"] = device["secret"]
            
            if (initial_read):
                
                try:
                    print("[i] add_device: CONNECTING TO DEVICE")
                    handler = Connector.connect(key = key, **connection_data)
                except Exception as e:
                    print(f"[i] add_device: Exception -> {e}")
                    raise NoConnectionPossibleException
                    
                show_commands = app.models.device_vendor_mapping[device_kind.value][vendor][model].MAP["show"]
                
                # Read device configurations and write them to the database
                print("[i] add_device: READING DEVICE DATA")
                for command_name, command_details in show_commands.items():
                    print(f"[i] add_device: RUNNING {command_name}")
                    function = command_details["func"]
                    result = function(handler=handler)
                    
                    if command_details["db"]["write"] and result:    
                        print(f"[i] add_device: WRITING RESULT TO DATABASE")
                        print(f"[i] RESULT: ", result)
                        device={command_details["db"]["field"]: result}
                        CRUD.update(key = key, device_type = device_kind.value, device = device)
                        print(f"[i] add_device: WRITING RESULT TO DATABASE COMPLETE")
                print("[i] add_device: READING COMPLETE")
                
            print("[i] add_device: FINISHED")
            add_device = CRUD.read(key, device_kind.value)
            return {"detail": add_device}
        except NoConnectionPossibleException as e:
            print(e)
            CRUD.delete(key, device_kind.value)
            raise HTTPException(status_code=500, detail="No connection possible")
        except HostAlreadyExistsException as e:
            
            print(e)
            CRUD.delete(key, device_kind.value)
            raise HTTPException(status_code=406, detail="HostAlreadyExists")
        except Exception as e:
            print("add_device: ", traceback.format_exc())
            CRUD.delete(key, device_kind.value)
            raise HTTPException(status_code=500, detail="Error")
        
      
    @classmethod
    def reload_device(cls, key: str, device_kind: app.models.DeviceKinds, vendor: str, model: str):
        print("[i] reload_device: RELOADING DEVICE DATA")
        handlers = Connect.get_handlers()
        if key not in handlers[device_kind.value]:
            print("[!] reload_device: Exception - No Connection established")
            raise HTTPException(status_code=406, detail="No Connection established")
            
        handler = handlers[device_kind.value][key]["handler"]
        
        show_commands = app.models.device_vendor_mapping[device_kind.value][vendor][model].MAP["show"]
        # Read device configurations and write them to the database
        print("[i] reload_device: RUNNING RELOAD FUNCTIONS")
        for command_name, command_details in show_commands.items():
            print(f"[i] reload_device: RUNNING {command_name}")
            function = command_details["func"]
            result = function(handler=handler)
            print(f"[i] reload_device: {result=}")
            if (command_details["db"]["write"] and result) or (command_details["db"]["write"] and result == {}):    
                print(f"[i] reload_device: WRITING RESULT TO DATABASE")
                print(f"[i] reload_device: RESULT {result=}")
                
                device={command_details["db"]["field"]: result}
                CRUD.update(key = key, device_type = device_kind.value, device = device)
                print(f"[i] reload_device: WRITING RESULT TO DATABASE COMPLETE")
        print("[i] reload_device: RELOADING COMPLETED")
        
        reloaded_device = CRUD.read(key = key, device_type = device_kind.value)
        return {"detail": reloaded_device}
         
    @classmethod           
    def delete_device(cls, key: str, device_kind: app.models.DeviceKinds) -> Dict[str, str]:
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
            CRUD.delete(key, device_kind.value)
            return {"detail": True}
        except Exception as e:
            raise HTTPException(status_code=500, detail="Exception :See logs")

    @classmethod
    def update_device(cls, key: str, device_kind: app.models.DeviceKinds, device: app.schemas.DeviceUpdate):
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
        print("[i] Device - update_device: Called")
        try:
            print("[i] Device - update_device: Reading device")
            current_device = CRUD.read(key=key, device_type=device_kind)
            for document_key, value in device.dict().items():
                if value and type(value) is str:
                    current_device[document_key] = value
                elif type(value) is dict:
                    for sub_document_key, sub_value in value.items():
                        if sub_value and type(sub_value) is str:
                            current_device[document_key][sub_document_key] = sub_value
            CRUD.update(key=key, device_type=device_kind, device=current_device)
            return {"detail": True}
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Exception")
    
    @classmethod 
    def get_device(cls, key: str, device_kind: app.models.DeviceKinds):
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
        print("[i] Device - get_device: Called")
        try:
            print("[i] Device - get_device: Reading database")
            data=CRUD.read(key = key, device_type = device_kind.value)
            if data:
                print(f"[i] Device - get_device: Returning {data=}")
                return data
            raise NoSuchDeviceException
        except NoSuchDeviceException as e:
            print("[i] Device - get_device: No such device")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="NoSuchDeviceException")
        except Exception:
            print("[i] Device - get_device: Exception occured")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Exception")
    
    @classmethod
    def get_all_devices(cls, device_kind: app.models.DeviceKinds):
        """Returns all devices of type `device_kind`

        Args:
            device_kind (app.models.DeviceKinds): Supported device kinds

        Raises:
            Exception: Raised in case of an unknown error

        Returns:
            dict: All stored devices of `device_kind`
        """
        try:
            print("[i] Device - get_all_devices: Called")
            data=CRUD.read_collection(device_kind.value)
            print("[i] Device - get_all_devices: Reading database")
            for device in data:
                device.pop("_id")
            print(f"[i] Device - get_all_devices: Returning {data=}")
            return data
        except Exception:
            print("[i] Device - get_all_devices: Exception occured")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Exception")
