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
from app.core import autodetect
import netmiko


#TODO - Autodetect https://linuxtut.com/en/feff470e0093d0b7ca43/

class Connect:
    """Implements the 'connect' routers"""
    #db: dict = Depends(db_handler.get_instance) #CRUD instead
    handlers: dict = Handler.get_handlers()
    
    @classmethod
    def get_serial_ports(cls):
        """Returns available ports on server

        Returns:
            dict: Available ports
        """
        print("[i] Connect - connect: Retrieving serial ports")
        ports = Connector.list_serial_ports()
        print("[i] Connect - connect: Serial ports retrieved")
        return {"ports": ports}

    @classmethod
    def connect(cls, key: str, device_kind: app.models.DeviceKinds,
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
        print("[i] Connect - connect")
        if key in cls.handlers[device_kind.value]:
            print("[!] Connect - connect: Exception occured -> Connection already established")
            raise HTTPException(status_code=406, detail="Connection already established")
        
        host_data = CRUD.read(key = key, device_type = device_kind.value)
        if not host_data:
            print("[!] Connect - connect: Exception occured -> Host does not exist")
            raise HTTPException(status_code = 406, detail = "Host does not exist")

        # if not host_data["secret"]:
        #     print("[!] Connect - connect: Exception occured -> Secret password is missing")
        #     raise HTTPException(status_code = 406, detail = "Secret password is missing")
        

        if connection_type.value == "serial":
            print("[i] Connect - connect: Extracting serial connection data")
            # for key, value in host_data["serial"].items():
            #     if not value:
            #         raise HTTPException(status_code = 406, detail = f"MissingConnectionData: {key}")
                
            if port not in Connector.list_serial_ports():
                raise HTTPException(status_code = 406, detail = "PortDoesNotExistException")
            connection_data = host_data[connection_type.value]
            connection_data["secret"] = host_data["secret"]
            connection_data["serial_settings"] = {"port": port}
        elif connection_type.value in ("ssh", "telnet"):
            print("[i] Connect - connect: Extracting remote connection data")
            connection_data = host_data[connection_type.value]
            connection_data["secret"] = secret
            if port:
                connection_data["port"] = port

        try:
            print("[i] Connect - connect: Connecting")
            print(f"[i] Connect - connect: Connection data - {connection_data=}")
            #TODO - change type of port from int to str - check if it still works
            handler = Connector.connect(key = key, **connection_data)
            print("[i] Connect - connect: Connection successful")
            #self.loggers.open(key, key+".log")
        except netmiko.exceptions.NetmikoTimeoutException:
            print("[!] Connect - connect: Timeout occured")
            raise HTTPException(status_code = 500, detail = "Timeout occured")
        except ValueError:
            print("[!] Connect - connect: Device not supported")
            raise HTTPException(status_code = 500, detail = "Device not supported")
        except Exception as general_exception:
            print(f"[!] Connect - connect: Exception occured")
            print(general_exception)
            raise HTTPException(status_code = 500, detail = "Exception")

        if key not in cls.handlers[device_kind.value]:
            cls.handlers[device_kind.value][key] = {}
        cls.handlers[device_kind.value][key]["handler"] = handler
        return {"detail": True}

    @classmethod
    def disconnect(cls, key: str, device_kind: app.models.DeviceKinds):
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
        print("[i] Connect - disconnect")
        if not key in cls.handlers[device_kind.value].keys():
            raise HTTPException(status_code = 406, detail = "HandlerNotFound")
        try:
            print("[i] Connect - disconnect: Disconnecting")
            cls.handlers[device_kind.value][key]["handler"].disconnect()
            cls.handlers[device_kind.value].pop(key)
            print("[i] Connect - disconnect: Disconnection successful")
            return {"detail": True}
        except Exception as general_exception:
            print("[i] Connect - disconnect: Exception occured")
            print(general_exception)
            raise HTTPException(status_code = 500, detail = "Exception")

    @classmethod
    def get_connections_frontend(cls):
        #print(f"[i] Connect - get_connections_frontend: {cls.handlers}")
        res = {}
        for device_type, handler_dict in cls.handlers.items():
            #print(f"[i] Connect - get_handlers: {device_type=} {handler_dict=}")
            res[device_type] = list(handler_dict.keys())
        #print(f"[i] Connect - get_connections_frontend: {res=}")
        return {"detail": res}
    
    @classmethod
    def get_handlers(cls):
        print("[i] Connect - get_handlers")
        return cls.handlers