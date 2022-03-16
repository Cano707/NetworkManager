from typing import Any, Dict, Union
from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv
from app.api.v1.handlers import Handlers
from app.database import db as db_handler
import app.models

command_router=APIRouter()

#TODO - Redo the whole fucking thing!
#TODO - Refactoring
#TODO - Plastic surgery
#TODO - Exception handling
@cbv(command_router)
class CommandCBV:
    db: dict = Depends(db_handler.read)
    handlers: dict = Depends(Handlers.get_handlers)
    
    def __init__(self):
        pass
    
    def get_host_details(self, key: str, device_kind: app.models.DeviceKinds) -> Dict[str, str]:
        """Return vendor and model of host

        Args:
            key (str): Specifies host
            device_kind (app.models.DeviceKinds): Supported device kinds

        Returns:
            dict: vendor and model of host
        """
        host=self.db[device_kind.value][key]
        vendor=host["vendor"]
        model=host["model"]
        return {"vendor": vendor, "model": model}
    
    @command_router.get("/{device_kind}/{key}")
    def get_command_types(self, key: str, device_kind: app.models.DeviceKinds) -> Dict[str, list]:
        """Returns available commands for model of specified host (`key`)

        Args:
            key (str): Specifies device
            device_kind (app.models.DeviceKinds): Supported device kinds

        Raises:
            HostDoesNotExistException: Raised if device under `key` does not exist

        Returns:
            Dict[str, list]: List of available command types
        """
        if key not in self.db[device_kind.value].keys():
            raise HTTPException(status_code=406, detail=f"HostDoesNotExistException")
        host_details=self.get_host_details(key=key, device_kind=device_kind)
        model_command_map=app.models.device_vendor_mapping[device_kind.value][host_details["vendor"]][host_details["model"]].MAP
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
        host_details=self.get_host_details(key=key, device_kind=device_kind)
        model_commands=list(app.models.device_vendor_mapping[device_kind.value][host_details["vendor"]][host_details["model"]].MAP[type].keys())
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
        
        host_details=self.get_host_details(key=key, device_kind=device_kind)
        command=app.models.device_vendor_mapping[device_kind][host_details["vendor"]][host_details["model"]].MAP[type][command]
     
        args=command["args"]
        opts=command["opts"]
        return {"args": args, "opts": opts}
    
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
            InvalidArgumentsException: Raised if arguments are invalid
            CommandDoesNotExistException: Raised if `command` does not exist

        Returns:
            Dict[str, Any]: Result of `command`
        """
        host_details=self.get_host_details(key=key, device_kind=device_kind)
        commands=self.get_commands(key=key, device_kind=device_kind, type=type)["detail"]
        if command not in commands:
            raise HTTPException(status_code=406, detail="CommandDoesNotExistException")
        
        command_details=app.models.device_vendor_mapping[device_kind.value][host_details["vendor"]][host_details["model"]].MAP[type][command]
        
        if not self.validate_command(mandatory_args=command_details["args"], optional_args=command_details["opts"], given_args=args_opts):
            raise HTTPException(status_code=400, detail="InvalidArgumentsException")
        
        handler=self.handlers[device_kind.value][key]
        try:
            function=command_details["func"]
        except Exception as e:
            raise HTTPException(status_code=500, detail="Exception")
        result=function(handler=handler, **args_opts)
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
        
        