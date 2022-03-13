from typing import Dict
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
    
    def get_host_details(self, key: str, device_kind: app.models.DeviceKinds):
        host=self.db[device_kind.value][key]
        vendor=host["vendor"]
        model=host["model"]
        return {"vendor": vendor, "model": model}
    
    @command_router.get("/{device_kind}/{key}/get-available-command-types")
    def get_command_types(self, key: str, device_kind: app.models.DeviceKinds):
        if key not in self.db[device_kind.value].keys():
            raise HTTPException(status_code=406, detail=f"Host {key} does not exit.")
            #return {"error": f"Host {key} does not exit."}
        host_details=self.get_host_details(key=key, device_kind=device_kind)
        model_command_map=app.models.device_vendor_mapping[device_kind.value][host_details["vendor"]][host_details["model"]].MAP
        model_command_types=list(model_command_map.keys())
        return {"types": model_command_types}
    
    @command_router.get("/{device_kind}/{key}/get-commands/{type}")
    def get_commands(self, key: str, device_kind: app.models.DeviceKinds, type: str):
        """
        if key not in self.db[device_kind.value].keys():
            return {"error": f"Host {key} does not exit."}
        host=self.db[device_kind.value][key]
        vendor=host["vendor"]
        model=host["model"]
        model_map=app.models.device_vendor_mapping[device_kind.value][vendor][model].MAP
        model_types=list(model_map.keys())
        """
        model_command_types=self.get_command_types(key=key, device_kind=device_kind)
        if type not in model_command_types["types"]:
            raise HTTPException(status_code=406, detail=f"Commands of type {type} do not exit.")
        host_details=self.get_host_details(key=key, device_kind=device_kind)
        model_commands=list(app.models.device_vendor_mapping[device_kind.value][host_details["vendor"]][host_details["model"]].MAP[type].keys())
        return {"commands": model_commands}
    
    @command_router.get("/{device_kind}/{key}/get-command-details/{type}/{command}")
    def get_command_details(self, key: str, device_kind: app.models.DeviceKinds, type: str, command: str):
        """
        if key not in self.db[device_kind.value].keys():
            return {"error": f"Host {key} does not exit."}
        host=self.db[device_kind.value][key]
        vendor=host["vendor"]
        model=host["model"]
        model_map=app.models.device_vendor_mapping[device_kind.value][vendor][model].MAP
        model_types=list(model_map.keys())
        if type not in model_types:
            return {"error": f"Commands of type {type} do not exit."}
        commands=model_map[type]
        """
        host_details=self.get_host_details(key=key, device_kind=device_kind)
        commands=app.models.device_vendor_mapping[device_kind.value][host_details["vendor"]][host_details["model"]].MAP[type]
        if command not in commands.keys():
            raise HTTPException(status_code=406, detail=f"Command {command} does not exit.")
        command=commands[command]
        args=list()
        opt=list()
        if "args" in command.keys():
            args=command["args"]
        if "opt" in command.keys():
            opt=command["opt"]
        return {"args": args, "opt": opt}
    
    @command_router.post("/{device_kind}/{key}/execute/{type}/{command}")
    def execute_command(self, device_kind: app.models.DeviceKinds, key: str, type: str, command: str, args_opts: dict):
        host_details=self.get_host_details(key=key, device_kind=device_kind)
        #command_details=self.get_command_details(key=key, device_kind=device_kind, type=type, command=command)
        commands=app.models.device_vendor_mapping[device_kind.value][host_details["vendor"]][host_details["model"]].MAP[type]
        if command not in commands.keys():
            raise HTTPException(status_code=406, detail=f"Command {command} does not exit.")
        command_details=commands[command]
        if "args" in command_details.keys() and not self.validate_command(mandatory_args=command_details["args"], given_args=args_opts):
            raise HTTPException(status_code=400, detail=f"missing arguments")
        handler=self.handlers[device_kind.value][key]
        function=commands[command]["func"]
        result=function(handler=handler, **args_opts)
        return result
        
    #TODO - What arguments are missing?
    def validate_command(self, mandatory_args: dict, given_args: dict):
        mandatory_args=mandatory_args
        given_args_opts=given_args.keys()
        not_valid=set(mandatory_args) - set(given_args_opts)
        if not_valid:
            return False
        return True
        
        