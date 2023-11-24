import traceback
from typing import Any, Dict, Tuple, Union
from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv
from app.core.handlers import Handler
import app.models
from app.crud.crud import CRUD


class Command:
    handlers: dict = Handler.get_handlers()

    def __init__(self):
        pass

    @classmethod
    def extract_vendor_model(cls, key: str, device_kind: app.models.DeviceKinds) -> Tuple[str]:
        """Return vendor and model of host

        Args:
            key (str): Specifies host
            device_kind (app.models.DeviceKinds): Supported device kinds

        Returns:
            dict: vendor and model of host
        """
        #host=cls.db[device_kind.value].find_one({"key": key})
        host = CRUD.read(key=key, device_type = device_kind.value)
        if not host:
            print("[!] Command - extract_vendor_model: Host does not exist")
            raise HTTPException(status_code=406, detail=f"Host does not exist")
        vendor=host["vendor"]
        model=host["model"]
        return vendor, model

    @classmethod
    def get_command_types(cls, key: str, device_kind: app.models.DeviceKinds) -> Dict[str, list]:  
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
            vendor, model = cls.extract_vendor_model(key, device_kind)
        except Exception as e:
            print(e)
            raise
        model_command_map=app.models.device_vendor_mapping[device_kind.value][vendor][model].MAP
        model_command_types=list(model_command_map.keys())
        return {"detail": model_command_types}

    @classmethod
    def get_commands(cls, key: str, device_kind: app.models.DeviceKinds, 
                     type: str) -> Dict[str, list]:
        """Returns available commands for specified hsost (`key`)

        Args:
            key (str): Specifies device
            device_kind (app.models.DeviceKinds): Supported device kinds
            type (str): Command type

        Raises:
            CommandTypeDoesNotExist: Raised if `type` does not exist

        Returns:
            Dict[str, list]: List of available commands
        """
        model_command_types=cls.get_command_types(key=key, device_kind=device_kind)["detail"]
        if type not in model_command_types:
            raise HTTPException(status_code=406, detail=f"CommandTypeDoesNotExist")
        vendor, model=cls.extract_vendor_model(key, device_kind)
        model_commands=list(app.models.device_vendor_mapping[device_kind.value][vendor][model].MAP[type].keys())
        return {"detail": model_commands}

    @classmethod
    def get_command_details(cls, key: str, device_kind: app.models.DeviceKinds, type: str, command: str) -> dict[str, Union[str, list]]:
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
        commands=cls.get_commands(key=key, device_kind=device_kind, type=type)["detail"]
        if command not in commands:
            raise HTTPException(status_code=406, detail="CommandDoesNotExist")

        vendor, model=cls.extract_vendor_model(key, device_kind)
        command=app.models.device_vendor_mapping[device_kind][vendor][model].MAP[type][command]

        res={k:v for k, v in command.items() if k != "func" and "callback" not in v}

        return res

    @classmethod
    def execute_command(cls, key: str, device_kind: app.models.DeviceKinds, type: str, command: str, args_opts: dict) -> Dict[str, Any]:
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
        print("[i] Command - execute_command: Preparing execution")
        print(f"[!] Command - execute_command: Looking up -> {command=}")
        vendor, model=cls.extract_vendor_model(key=key, device_kind=device_kind)
        commands=cls.get_commands(key=key, device_kind=device_kind, type=type)["detail"]
        if command not in commands:
            print("[!] Command - execute_command: Execption occured -> Command does not exist")
            print("######### TRACEBACK #########") 
            print(traceback.format_exc())
            print("######### TRACEBACK #########")
            raise HTTPException(status_code=406, detail="Command does not exist")

        command_details=app.models.device_vendor_mapping[device_kind.value][vendor][model].MAP[type][command]
        
        if not cls.validate_command(mandatory_args=command_details["args"], optional_args=command_details["opts"], given_args=args_opts):
            print("[!] Command - execute_command: Execption occured -> Invalid arguments")
            print("######### TRACEBACK #########") 
            print(traceback.format_exc())
            print("######### TRACEBACK #########")
            raise HTTPException(status_code=406, detail="Invalid arguments")

        # COMMENT DUE TO TEST PURPOSE
        if key not in cls.handlers[device_kind.value]:  
            print("[!] Command - execute_command: Execption occured -> No established connection")
            print("######### TRACEBACK #########") 
            print(traceback.format_exc())
            print("######### TRACEBACK #########")
            raise HTTPException(status_code=406, detail="No established connection") 
        
        handler=cls.handlers[device_kind.value][key]["handler"]
        # COMMENT DUE TO TEST PURPOSE
        print(f"[i] Command - execute_command: command_details -> {command_details}")
        function=command_details["func"]
        try:
            result=function(handler=handler, **args_opts) 
        except Exception as e:
            print("[!] Command - execute_command: Execption occured -> No established connection")
            print("######### TRACEBACK #########") 
            print(traceback.format_exc())
            print("######### TRACEBACK #########")
            raise HTTPException(status_code=500, detail="Exception")

        # #TODO Check for "update"   
        print("[i] Command - execute_command: Checking for callback")
        if command_details["db"]["write"] and result:
            print("[!] Command - execute_command: Callback found")
            if command_details["db"]["update"]:
                result = command_details["db"]["callback"](handler)
            device={command_details["db"]["field"]: result}

            CRUD.update(key = key, device_type = device_kind.value, device = device)
            print("[!] Command - execute_command: Update completed")
        return {"detail": result}

    #TODO - What arguments are missing?
    #TODO - Options can depend on each other. For example, option a is optional if not present but requires option b to be set when a itcls is set
    def validate_command(mandatory_args: list, optional_args: list, given_args: dict) -> bool:
        """Validates arguments for command to execute

        Args:
            mandatory_args (list): Mandatory arguments
            optional_args (list): Optional arguements
            given_args (dict): Given arguemnts

        Returns:
            bool: Valid (true) or Invalid (false)
        """
        print
        (f"[i] Command - validate_command: {given_args=}")
        print(f"[i] Command - validate_command: {mandatory_args=}")
        given_args_keys=given_args.keys()
        if set(mandatory_args)-set(given_args_keys):
            return False
        if (set(given_args_keys)-set(mandatory_args))-set(optional_args):
            return False
        return True