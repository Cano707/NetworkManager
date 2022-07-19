from typing import Any, Dict, Tuple, Union
from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv
from app.core.handlers import Handler
from app.database import db as db_handler
import app.models
from app.crud.crud import CRUD
from app.core import DeviceLogger
from os import path
from datetime import datetime

command_router=APIRouter()

#TODO - Refactoring
#TODO - Exception handling
@cbv(command_router)
class CommandCBV:
    db: dict = Depends(db_handler.get_instance)
    handlers: dict = Depends(Handler.get_handlers)
    
    def __init__(self):
        pass
    
    def extract_vendor_model(self, key: str, device_kind: app.models.DeviceKinds) -> Tuple[str]:
        """Return vendor and model of host

        Args:
            key (str): Specifies host
            device_kind (app.models.DeviceKinds): Supported device kinds

        Returns:
            dict: vendor and model of host
        """
        host=self.db[device_kind.value].find_one({"key": key})
        if not host:
            raise HTTPException(status_code=406, detail=f"HostDoesNotExist")
        vendor=host["vendor"]
        model=host["model"]
        return vendor, model
    
    @command_router.get("/{device_kind}/{key}")
    def get_command_types(self, key: str, device_kind: app.models.DeviceKinds) -> Dict[str, list]:
        """Returns available commands for model of specified host (`key`)

        Args:
            key (str): Specifies device
            device_kind (app.models.DeviceKinds): Supported device kinds

        Raises:
            HostDoesNotExist: Raised if device under `key` does not exist

        Returns:
            Dict[str, list]: List of available command types
        """
        try:
            vendor, model = self.extract_vendor_model(key, device_kind)
        except Exception as e:
            print(e)
            raise
        model_command_map=app.models.device_vendor_mapping[device_kind.value][vendor][model].MAP
        model_command_types=list(model_command_map.keys())
        return {"detail": model_command_types}
    
    @command_router.get("/{device_kind}/{key}/{type}")
    def get_commands(self, key: str, device_kind: app.models.DeviceKinds, type: str) -> Dict[str, list]:
        """Returns available commands for specified host (`key`)

        Args:
            key (str): Specifies device
            device_kind (app.models.DeviceKinds): Supported device kinds
            type (str): Command type

        Raises:
            CommandTypeDoesNotExist: Raised if `type` does not exist

        Returns:
            Dict[str, list]: List of available commands
        """
        model_command_types=self.get_command_types(key=key, device_kind=device_kind)["detail"]
        if type not in model_command_types:
            raise HTTPException(status_code=406, detail=f"CommandTypeDoesNotExist")
        vendor, model=self.extract_vendor_model(key, device_kind)
        model_commands=list(app.models.device_vendor_mapping[device_kind.value][vendor][model].MAP[type].keys())
        return {"detail": model_commands}
    
    @command_router.get("/{device_kind}/{key}/{type}/{command}")
    def get_command_details(self, key: str, device_kind: app.models.DeviceKinds, type: str, command: str) -> dict[str, Union[str, list]]:
        """Returns mandatory and optional arguments for `command`

        Args:
            key (str): Specifies device
            device_kind (app.models.DeviceKinds): Supported device kinds
            type (str): Command type
            command (str): Command 

        Raises:
            CommandDoesNotExist: Raised if command does not exist

        Returns:
            dict[str, Union[str, list]]: Mandatory (args) and optional (opts) arguments for command
        """
        commands=self.get_commands(key=key, device_kind=device_kind, type=type)["detail"]
        if command not in commands:
            raise HTTPException(status_code=406, detail="CommandDoesNotExist")
        
        vendor, model=self.extract_vendor_model(key, device_kind)
        command=app.models.device_vendor_mapping[device_kind][vendor][model].MAP[type][command]
     
        #command.pop("func")
        res={k:v for k, v in command.items() if k != "func"}
     
        return res
    
    @command_router.post("/{device_kind}/{key}/{type}/{command}")
    def execute_command(self, key: str, device_kind: app.models.DeviceKinds, type: str, command: str, args_opts: dict) -> Dict[str, Any]:
        """Executes command and returns result, if result exists

        Args:
            key (str): Specifies device
            device_kind (app.models.DeviceKinds): Supported device kinds
            type (str): Command type
            command (str): Command 
            args_opts (dict): Mandatory and optional arguments to pass to `command`

        Raises:
            Exception: Raised in case of an unknown error
            InvalidArguments: Raised if arguments are invalid
            CommandDoesNotExist: Raised if `command` does not exist

        Returns:
            Dict[str, Any]: Result of `command`
        """        
        vendor, model=self.extract_vendor_model(key=key, device_kind=device_kind)
        commands=self.get_commands(key=key, device_kind=device_kind, type=type)["detail"]
        if command not in commands:
            raise HTTPException(status_code=406, detail="CommandDoesNotExist")
        
        command_details=app.models.device_vendor_mapping[device_kind.value][vendor][model].MAP[type][command]
        if not self.validate_command(mandatory_args=command_details["args"], optional_args=command_details["opts"], given_args=args_opts):
            raise HTTPException(status_code=400, detail="InvalidArguments")
        
        try:
            handler=self.handlers[device_kind.value][key]["handler"]
        except KeyError:
            raise HTTPException(status_code=400, detail="NoConnection")
        
        function=command_details["func"]
        try:
            result=function(handler=handler, **args_opts)
            log_msg = f"{datetime.now().strftime('%d.%m.%Y %H:%M:%S')} - command: {command} - params: {args_opts} "
            DeviceLogger.write(key, log_msg)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Exception")
        
        if command_details["db"]["write"]:
            device={command_details["db"]["field"]: result}
            CRUD.update(key=key, device_type=device_kind, device=device)
        return {"detail": result}
        
    #TODO - What arguments are missing?
    #TODO - Options can depend on each other. For example, option a is optional if not present but requires option b to be set when a itself is set
    def validate_command(self, mandatory_args: list, optional_args: list, given_args: dict) -> bool:
        """Validates arguments for command to execute

        Args:
            mandatory_args (list): Mandatory arguments
            optional_args (list): Optional arguements
            given_args (dict): Given arguemnts 

        Returns:
            bool: Valid (true) or Invalid (false)
        """
        given_args_keys=given_args.keys()
        if set(mandatory_args)-set(given_args_keys):
            return False
        if (set(given_args_keys)-set(mandatory_args))-set(optional_args):
            return False
        return True