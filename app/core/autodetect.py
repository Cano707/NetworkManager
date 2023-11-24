import re
from app.models import autodetect_device_vendor_mapping
import app.schemas
from typing import List
from app.core.exceptions import MissingConnectionData, ConnectionError
from app.core.connector import Connector
import app.models
from app.models import autodetect_device_vendor_mapping
from app.schemas import ConnectionType
from netmiko.ssh_autodetect import SSHDetect

"""
netmiko ssh detect wont be necessary since once i know which vendor this 
device is from i know which device_type to 


- if device_type in connection_type is set then netmiko wont be neccessary
    - check if host, username and password
    - connect
    - check device_type for vendor
    - continue 
- if device_type in connection_type is not set then netmiko will be neccessary
    - check if host, username and password were given 
    - run netmiko guesser
    - select best guess
    - continue with vendor and model check
- run vendor model check 
    #TODO vendor model mapping neccessary - in models 
    - iterate over all vendors and models 
        - check if given model 

"""

class AutoDetector:
    
    def __init__(self):
        pass
    
    @classmethod
    def detect(cls, handler): 
        pass
        
    @classmethod
    def run(cls, key: str, device: app.schemas.Device, device_kind: app.models.DeviceKinds): 
        connection_data=device["ssh"]
        if not (connection_data["host"] and connection_data["username"] and connection_data["password"]):
                raise MissingConnectionData
        
        
        guess = None
        if not connection_data["device_type"]:
            connection_data["device_type"] = "autodetect"
            guess = Connector.guesser(**connection_data)
            connection_data["device_type"] = guess
    
        connection_data["secret"] = device["secret"]
    
        try:
            handler=Connector.connect(key = key, **connection_data)
        except Exception as e:
            raise ConnectionError
   
        
        autodetect_vendor_mapping=autodetect_device_vendor_mapping[device_kind]
        if connection_data["device_type"]: 
            for vendor, func_models in autodetect_vendor_mapping.items():
                pids = func_models["func"](handler = handler)
                for model, doc in func_models["models"].items():
                    if doc in pids:
                        return vendor, model, guess
                        
                        
        
         
            
            
            
  
        
    
    @classmethod
    def check_available_connection_types(cls, device: app.schemas.Device) -> List[str]: 
        available_connections=["serial"]
        
        # Check for ssh
        connection_data=device["ssh"]
        if (connection_data["username"] and connection_data["password"] and connection_data["host"]):
            available_connections.append("ssh")
            
        # Check for telnet
        connection_data=device["telnet"]
        if connection_data["host"]:
            available_connections.append("telnet")
            
        return available_connections
            
        