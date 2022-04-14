from pydantic import BaseModel
from typing import Optional, Union
from enum import Enum
from app.models import device_vendor_mapping
from netmiko.ssh_dispatcher import CLASS_MAPPER


#TODO - Extract all ssh for SSHCredentials and so on... Such that SSHCredentials.device_type_netmiko only maps ssh devices
#TODO - Currently fastapi does not support custom typing. For the time being, the device_type_netmiko will be a string which then will be 
#       verified at post 
class SSHCredentials(BaseModel): 
    username: str = ""
    password: str = ""
    host: str = ""
    port: str = ""
    device_type: str = ""
    
class TelnetCredentials(BaseModel): 
    username: str = ""
    password: str = ""
    host: str = ""
    port: str = ""
    device_type: str = ""
    
class SerialCredentials(BaseModel): 
    username: str = ""
    password: str = ""
    device_type: str = ""

class Device(BaseModel):
    hostname: str = ""
    vendor: str = ""
    model: str = ""
    secret: Optional[str] = ""
    config: Optional[list] = list()
    ssh: Optional[SSHCredentials] = SSHCredentials()
    telnet: Optional[TelnetCredentials] = TelnetCredentials()
    serial: Optional[SerialCredentials] = SerialCredentials()

class DeviceUpdate(BaseModel): 
    hostname: Optional[str] 
    vendor: Optional[str] 
    model: Optional[str] 
    secret: Optional[str] 
    ssh: Optional[SSHCredentials]
    telnet: Optional[TelnetCredentials] 
    serial: Optional[SerialCredentials] 
    