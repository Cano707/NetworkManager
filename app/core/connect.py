import sys
import serial
import glob
import netmiko
from enum import Enum

#TODO - Yet to implement and to embed
class DeviceTypesNetmiko(str, Enum):
    pass

class Connector:
    # Low level connection class
    def __init__(self):
        pass 

    @staticmethod
    def connect(**kwargs) -> netmiko.ConnectHandler:
        #TODO - Extend exceptions handling
        handler = None 
        # For the time being, this will be needed until the bug in netmiko is fixed. 
        # Issue is, that `handler.enable()` raises an exception claiming that `secret`
        # has not been given, although it has been. 
        kwargs["global_delay_factor"]=2
        #kwargs["session_log"]="netmiko_session.log"
        try:
            handler = netmiko.ConnectHandler(**kwargs)
        except Exception as e:
            print([f"[!] Exception: {e}"])
            raise e
        return handler

    @staticmethod
    def disconnect(handler: netmiko.ConnectHandler):
        handler.disconnect()
        
    @staticmethod
    def list_serial_ports() -> list:
        # https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z0-9]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result