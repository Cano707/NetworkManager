from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from app.database import db as db_handler
from app.core import Connector
from typing import Literal, Optional
import app.schemas
import app.models 
from app.api.v1.handlers import Handlers

connect_router=APIRouter()

#TODO - Refactoring
#TODO - Plastic surgery
#TODO - Exception handling
@cbv(connect_router)
class ConnectCBV:
    db: dict = Depends(db_handler.read)
    handlers: dict = Depends(Handlers.get_handlers)
    
    def __init__(self):
        pass
    
    @connect_router.get("/ports")
    def get_serial_ports(self):
        ports=Connector.list_serial_ports()
        return {"ports": ports}
    
    #TODO - SSH/Telnet yet to be implemented
    @connect_router.post("/{device_kind}/{key}/new-connection/{connection_type}")
    def connect(self, key: str, device_kind: app.models.DeviceKinds, connection_type: app.schemas.ConnectionType, port: Optional[str] = ""):
        if connection_type.value == "serial":
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
        elif connection_type.value == "ssh" or connection_type.value == "telnet":
            if not key in self.db[device_kind.value]:
                return {"Error": f"Host {key} does not exit."}
            host=self.db[device_kind.value][key]
            connection_data=host[connection_type.value]
            if connection_type.value == "ssh" or connection_type.value == "telnet":
                if not (connection_data[connection_type.value]["username"] or 
                        connection_data[connection_type.value]["password"] or
                        connection_data[connection_type.value]["host"] or
                        connection_data[connection_type.value]["port"]):
                    return {"Error": "Missing connection data."}
                # Connect
            return {"message": "success"}
    
    @connect_router.post("/{device_kind}/{key}/disconnect")
    def disconnect(self, key: str, device_kind: app.models.DeviceKinds):
        if key in self.handlers.keys():
            self.handlers[key].disconnect()
            return {"detail": "success"}
        return {"detail": "failure"}
            
        
    """
    #TODO - Fuse this and next method
    @connect_router.post("/{device_kind}/{key}/new-connection/remote/{connection_type}")
    def connect_remote(self, key: str, device_kind: app.models.DeviceKinds, connection_type: app.schemas.ConnectionType): 
        if not key in self.db[device_kind.value]:
            return {"Error": f"Host {key} does not exit."}
        host=self.db[device_kind.value][key]
        connection_data=host[connection_type.value]
        if connection_type.value == "ssh" or connection_type.value == "telnet":
            if not (connection_data[connection_type.value]["username"] or 
                    connection_data[connection_type.value]["password"] or
                    connection_data[connection_type.value]["host"] or
                    connection_data[connection_type.value]["port"]):
                return {"Error": "Missing connection data."}
            # Connect
        return {"message": "success"}

    @connect_router.post("/{device_kind}/{key}/new-connection/serial")
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
    """
    
 
    