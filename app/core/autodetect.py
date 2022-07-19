import re
from app.models import autodetect_device_vendor_mapping
import app.schemas
from typing import List

"""
netmiko ssh detect wont be necessary since once i know which vendor this 
device is from i know which device_type to 
"""

class AutoDetector:
    REGEX = r"(?:PID.+)"
    
    def __init__(self):
        pass
    
    @classmethod
    def detect(cls, handler): 
        pattern=cls.REGEX + f"({expr})"
        
    @classmethod
    def run(cls, device: app.schemas.Device): 
        available_connections=cls.check_available_connection_types(device)
        
    
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
            
        