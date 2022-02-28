from pydantic import BaseModel
from typing import Optional
from enum import Enum
from app.models import device_vendor_mapping

#TODO - Wrong. Look at Swagger instead of vendor device type is shown
Vendors=Enum("Vendors", [(vendor, vendor) for vendor in device_vendor_mapping.keys()])

class DeviceKinds(str,Enum):
    router="router"
    switch="switch"

class SSHCredentials(BaseModel): 
    username: str
    password: str
    host: str
    port: int
    
class TelnetCredentials(BaseModel): 
    username: str
    password: str
    host: str
    port: int
    
class SerialCredentials(BaseModel): 
    username: str
    password: str

class Device(BaseModel):
    hostname: str
    vendor: str
    model: str
    secret: Optional[str] = ""
    ssh: Optional[SSHCredentials] = SSHCredentials(username="", password="", host="", port=0)
    telnet: Optional[TelnetCredentials] = TelnetCredentials(username="", password="", host="", port=0)
    serial: Optional[SerialCredentials] = SerialCredentials(username="", password="")
    
class DeviceResponse(Device): 
    pass

class DeviceUpdate(BaseModel): 
    hostname: Optional[str]
    vendor: Optional[str]
    model: Optional[str]
    secret: Optional[str] = ""
    ssh: Optional[SSHCredentials] = SSHCredentials(username="", password="", host="", port=0)
    telnet: Optional[TelnetCredentials] = TelnetCredentials(username="", password="", host="", port=0)
    serial: Optional[SerialCredentials] = SerialCredentials(username="", password="")
    