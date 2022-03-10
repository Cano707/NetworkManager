from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from app.database import db as db_handler
from app.core import Connector
from typing import Literal, Optional
from app.schemas import ConnectionType
import app.models 
from app.api.v1.handlers import Handlers

connect_router=APIRouter()

@cbv(connect_router)
class ConnectCBV:
    db: dict = Depends(db_handler.read)
    handlers: dict = Depends(Handlers.get_handlers)
    
    def __init__(self):
        #self.handlers=dict()
        #for device_type in app.models.device_vendor_mapping.keys():
        #    self.handlers[device_type]=dict()
        pass
    
    @connect_router.post("/{device_kind}/new-connection/remote/{connection_type}/{key}")
    def connect_remote(self, key: str, device_kind: app.models.DeviceKinds, connection_type: ConnectionType): 
        if not key in self.db[device_kind.value]:
            return {"Error": f"Host {key} does not exit."}
        host=self.db[device_kind.value][key]
        #TODO - are username and password necessary for serial login?
        connection_data=host[connection_type.value]
        if connection_type.value == "ssh" or connection_type.value == "telnet":
            if not (connection_data[connection_type.value]["username"] or 
                    connection_data[connection_type.value]["password"] or
                    connection_data[connection_type.value]["host"] or
                    connection_data[connection_type.value]["port"]):
                return {"Error": "Missing connection data."}
            # Connect
        return {"message": "success"}

    @connect_router.post("/{device_kind}/new-connection/serial/{key}")
    def connect_serial(self, key: str, device_kind: app.models.DeviceKinds, port: str):
        if port not in Connector.list_serial_ports():
            return {"Error": f"Port {port} could not be found."}
        host=self.db[device_kind.value][key]
        device_type_nemtiko=host["serial"]["device_type_netmiko"]
        username=host["serial"]["username"]
        password=host["serial"]["password"]
        secret=host["secret"]
        connection_data={
            "device_type": device_type_nemtiko,
            "username": username,
            "password": password,
            "secret": secret,
            "serial_settings": {
                "port": port
            }
        }
        try: 
            handler=Connector.connect(**connection_data)
        except Exception as e:
            return {"error": "Connection failed. See logs for more information."}
        self.handlers[device_kind.value][key]=handler
        return {"message": "success"}
    
    @connect_router.get("/ports")
    def get_serial_ports(self):
        ports=Connector.list_serial_ports()
        return {"ports": ports}
    
    