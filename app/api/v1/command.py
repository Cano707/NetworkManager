from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from app.api.v1.handlers import Handlers
from app.database import db as db_handler
import app.models

command_router=APIRouter()

@cbv(command_router)
class CommandCBV:
    db: dict = Depends(db_handler.read)
    handlers: dict = Depends(Handlers.get_handlers)
    
    def __init__(self):
        pass
    
    @command_router.get("/{device_kind}/get-available-commands/{key}")
    def get_available_commands(self, key: str, device_kind: app.models.DeviceKinds):
        if key not in self.handlers[device_kind].keys():
            return {"error": f"No connection with {key} has been established."}
        host=self.db[device_kind.value][key]
        vendor=host["vendor"]
        model=host["model"]
        device_interface=app.models.device_vendor_mapping[device_kind.value][vendor]