from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv
from app.database import db as db_handler
from app.core import Connector
from typing import Optional
import app.schemas
import app.models 
from app.api.v1.handlers import Handlers

connect_router=APIRouter()

@cbv(connect_router)
class ConnectCBV:
    db: dict = Depends(db_handler.read)
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
            DeviceDoesNotExistException: Raised if device under `key` does not exist
            PortDoesNotExistException: Raised if port is not available on server

        Returns:
            dict: success
        """
        if key not in self.db[device_kind.value]:
            raise HTTPException(status_code=406, detail=f"Host {key} does not exist.")
        
        if connection_type.value == "serial":
            if port not in Connector.list_serial_ports():
                raise HTTPException(status_code=406, detail=f"Port {port} could not be found")  
            host=self.db[device_kind.value][key]
            connection_data=host[connection_type.value]
            connection_data["secret"]=host["secret"]
            connection_data["serial_settings"]={"port": port}
        elif connection_type.value == "ssh" or connection_type.value == "telnet":
            host=self.db[device_kind.value][key]
            connection_data=host[connection_type.value]
            if port:
                connection_data["port"]=port
            
        try:
            handler=Connector.connect(**connection_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal Server Error. Please see logs for details.")
        
        self.handlers[device_kind.value][key]=handler
        return {"detail": "success"}
    
    @connect_router.post("/{device_kind}/{key}")
    def disconnect(self, key: str, device_kind: app.models.DeviceKinds):
        """Disconnects from host under `key`

        Args:
            key (str): Specifies device
            device_kind (app.models.DeviceKinds): Supported device kinds

        Raises:
            Exception: Raised in case of an unknown error
            DeviceDoesNotExistException: Raised if device under `key` does not exist

        Returns:
            _type_: _description_
        """
        if not key in self.handlers.keys():
            raise HTTPException(status_code=406, detail=f"Host {key} does not exist.")
        try:
            self.handlers[key].disconnect()
            return {"detail": "success"}
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal Server Error. Please see logs for details.")
        
            
    
 
    