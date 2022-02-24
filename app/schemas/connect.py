from pydantic import BaseModel
from typing import Optional, Union, Literal

class ConnectionDetails(BaseModel):
    hostname: str
    protocol: Literal["ssh", "serial", "telnet"]
    device_kind: Literal["router", "switch"]

class RemoteConnectionDetails(ConnectionDetails):
    host: Optional[str] = ""

class SerialConnectionDetails(ConnectionDetails):
    port: str
    baudrate: Optional[int] = 9600
    
class ConnectionDetailsWrapper(BaseModel):
    connection_detail: Union[RemoteConnectionDetails, SerialConnectionDetails]
    