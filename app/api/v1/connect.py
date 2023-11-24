"""Defines the 'connect' routes"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi_utils.cbv import cbv
#from app.database import db as db_handler
from app.core import Connector
import app.schemas
import app.models
from app.core.handlers import Handler
from app.crud.crud import CRUD
from app.core.connect_backend import Connect

connect_router = APIRouter()

#TODO - Autodetect https://linuxtut.com/en/feff470e0093d0b7ca43/

@cbv(connect_router)
class ConnectAPI:
    """Implements the 'connect' routers"""
    #db: dict = Depends(db_handler.get_instance) #CRUD instead
    
    @connect_router.get("/serial-ports")
    def get_serial_ports(self):
        """Returns available ports on server

        Returns:
            dict: Available ports
        """
        try:
            return Connect.get_serial_ports()
        except:
            raise

    @connect_router.post("/{device_kind}/{key}/{connection_type}")
    def connect(self, key: str, device_kind: app.models.DeviceKinds,
                connection_type: app.schemas.ConnectionType, secret: str,
                port: Optional[str] = ""):
        """Connects via `connection_type` to host specified by `key` and `device_kind`

        Args:
            key (str): Specifies device
            device_kind (app.models.DeviceKinds): Supported device kinds
            connection_type (app.schemas.ConnectionType): Supported connection types
            port (Optional[str], optional): Specifies port to use for connection. tty/USB port for
                                            serial and connection port for telnet/ssh.
                                            Defaults to "".

        Raises:
            Exception: Raised in case of an unknown error
            HostDoesNotExistException: Raised if device under `key` does not exist
            PortDoesNotExistException: Raised if port is not available on server

        Returns:
            dict : result
        """
        try:
            return Connect.connect(key = key, device_kind = device_kind, connection_type = connection_type, secret = secret, port = port, )
        except:
            raise
        
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
        try:
            return Connect.disconnect(key = key, device_kind = device_kind)
        except:
            raise
        
    @connect_router.get("/connections")
    def get_connections(self):
        try:
            #print("[i] ConnectAPI - get_connections: Processing request")
            return Connect.get_connections_frontend()
        except:
            raise