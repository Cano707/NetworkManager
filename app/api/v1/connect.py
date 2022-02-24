from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from app.database import db as db_handler
from app.core import Connector
from typing import Optional
from app.schemas import RemoteConnectionDetails, SerialConnectionDetails, ConnectionDetailsWrapper
import os

connect_router=APIRouter()

@cbv(connect_router)
class ConnectCBV:
    db: dict = Depends(db_handler.read)
    
    def __init__(self):
        self.handlers={"router": {}, "switch": {}}
        
    @connect_router.post("/{device_kind}/new-connection/{hostname}")
    def connect(self, connection_details: ConnectionDetailsWrapper): 
        if not connection_details.hostname in self.handlers[connection_details.device_kind]:
            return {"Error": f"Host {connection_details.hostname} does not exit."}
        data=dict()
        if connection_details.protocol == "serial":
            if not os.path.exists(connection_details.port):
                return {"Error": "Port {connection_details.port} does not exit."}
            data["device_type"]="cisco_ios_serial"
            data["serial_settings"]={
                
            }
    
    @connect_router.get("/ports")
    def get_serial_ports(self):
        ports=Connector.list_serial_ports()
        return {"ports": ports}
    
    