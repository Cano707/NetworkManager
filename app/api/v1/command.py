from typing import Any, Dict, Tuple, Union
from fastapi import APIRouter, HTTPException
from fastapi_utils.cbv import cbv
import app.models
from app.crud.crud import CRUD
from app.core.command_backend import Command



command_router=APIRouter()

#TODO - Refactoring
#TODO - Exception handling
@cbv(command_router)
class CommandAPI:

    def __init__(self):
        pass

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
        print("[i] CommandAPI - get_command_types: Request received")
        try:
            return Command.get_command_types(key=key, device_kind=device_kind)
        except:
            raise

    @command_router.get("/{device_kind}/{key}/{type}")
    def get_commands(self, key: str, device_kind: app.models.DeviceKinds, 
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
        print("[i] CommandAPI - get_commands: Request received")
        try:
            return Command.get_commands(key=key, device_kind=device_kind, type=type)
        except:
            raise

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
        print("[i] CommandAPI - get_command_details: Request received")
        try:
            return Command.get_command_details(key=key, device_kind=device_kind, type=type, command=command)
        except:
            raise

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
        print("[i] CommandAPI - execute_command: Request received")
        try:
            return Command.execute_command(key=key, device_kind=device_kind, type=type, command=command, args_opts=args_opts)
        except:
            raise