import sys
import serial
import glob
import netmiko
import os
from datetime import datetime
from app.core import Settings

class Connector:
    """Implements methods to connect and disconnect to a network device"""
    def __init__(self):
        pass 
    
    @staticmethod
    def guesser(**kwargs) -> str:
        try:
            guesser = netmiko.SSHDetect(**kwargs)
        except ValueError as v_error:
            raise ValueError(v_error.args[0])
        except Exception as e:
            print(f"[!] guesser Exception {e}")
            raise e
        best_match = guesser.autodetect()
        return best_match

    @staticmethod
    def connect(key: str, **kwargs) -> netmiko.ConnectHandler:
        """Connects to a device

        Raises:
            e: General Exception due to a connection error
            EnvironmentError: Raised when the running os is not supported

        Returns:
            netmiko.ConnectHandler: Handler representing the connection
        """
        #TODO - Extend exceptions handling
        handler = None 
          
        """
        #TODO CHECK THIS 
        For the time being, this will be needed until the bug in netmiko is fixed. Issue is, that `handler.enable()` raises an exception claiming that `secret` has not been given, although it has been and a higher delay factor somehow solves this.
        """
        kwargs["global_delay_factor"] = 2
        
        if key:
            path = os.path.join(Settings.DEVICE_LOG_PATH, key)
            directory_check = os.path.isdir(path)
            if not directory_check:
                os.mkdir(path)
                
            log_file_name = datetime.today().strftime("%d%m%Y") + ".log"
            kwargs["session_log"] = os.path.join(Settings.DEVICE_LOG_PATH, key, log_file_name)
            
        try:
            handler = netmiko.ConnectHandler(**kwargs)
        except Exception as e:
            raise e
        return handler

    @staticmethod
    def disconnect(handler: netmiko.ConnectHandler):
        """Disconnects from device"""
        handler.disconnect()
        

         
    @staticmethod
    def list_serial_ports() -> list:
        """Lists all available serial ports

        Raises:
            EnvironmentError: Raised if OS is not supported

        Returns:
            list: List of available ports
        """
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