from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv
from app.database import db as db_handler
from app.core import Connector
from typing import Optional
import app.schemas
import app.models 
from app.api.v1.handlers import Handlers
from app.crud.crud import CRUD

connect_router=APIRouter()

#TODO - Autodetect https://linuxtut.com/en/feff470e0093d0b7ca43/

@cbv(connect_router)
class ConnectCBV:
    db: dict = Depends(db_handler.get_instance) #CRUD instead
    handlers: dict = Depends(Handlers.get_handlers)

    @connect_router.get("/serial-ports")
    def get_serial_ports(self):
        """Returns available ports on server

        Returns:
            dict: Available ports
        """
        ports=Connector.list_serial_ports()
        return {"ports": ports}
    
    @connect_router.post("/{device_kind}/{key}/{connection_type}")
    def connect(self, key: str, device_kind: app.models.DeviceKinds, connection_type: app.schemas.ConnectionType, port: Optional[str] = ""):
        """Connects via `connection_type` to host specified by `key` and `device_kind`

        Args:
            key (str): Specifies device
            device_kind (app.models.DeviceKinds): Supported device kinds
            connection_type (app.schemas.ConnectionType): Supported connection types
            port (Optional[str], optional): Specifies port to use for connection. tty/USB port for serial and connection port for telnet/ssh. Defaults to "".

        Raises:
            Exception: Raised in case of an unknown error
            HostDoesNotExistException: Raised if device under `key` does not exist
            PortDoesNotExistException: Raised if port is not available on server

        Returns:
            dict: success
        """
        host_data=CRUD.read(key, device_kind.value)
        if not host_data:
            raise HTTPException(status_code=406, detail="HostDoesNotExistException")
        
        if connection_type.value == "serial":
            if port not in Connector.list_serial_ports():
                raise HTTPException(status_code=406, detail="PortDoesNotExistException")  
            connection_data=host_data[connection_type.value]
            connection_data["secret"]=host_data["secret"]
            connection_data["serial_settings"]={"port": port}
        elif connection_type.value == "ssh" or connection_type.value == "telnet":
            connection_data=host_data[connection_type.value]
            if port:
                connection_data["port"]=port
        
        connection_data["log_file"]="app/logs/"+key+".log"
        try:
            #TODO - change type of port from int to str - check if it still works
            handler=Connector.connect(**connection_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Exception")
        
        self.handlers[device_kind.value][key]=handler
        return {"detail": "success"}
    
    @connect_router.post("/{device_kind}/{key}")
    def disconnect(self, key: str, device_kind: app.models.DeviceKinds):
        """Disconnects from host under `key`

        Args:
            <br/>key (str): Specifies device
            <br/>device_kind (app.models.DeviceKinds): Supported device kinds

        Raises:
            <br/>Exception: Raised in case of an unknown error
            <br/>HandlerNotFound: Raised if handler for host 'key' was not found

        Returns:
            <br/>_type_: _description_
        """
        if not key in self.handlers[device_kind.value].keys():
            raise HTTPException(status_code=406, detail="HandlerNotFound")
        try:
            self.handlers[device_kind.value][key].disconnect()
            self.handlers[device_kind.value].pop(key)
            return {"detail": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail="Exception")
        
            
    
 
    