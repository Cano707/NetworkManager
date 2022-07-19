from io import TextIOWrapper
from os.path import exists
from os.path import join
import traceback
from app import LOG_DIR

class FileNotFoundException(Exception):
    pass

class DeviceLogger:
    loggers=dict()
    
    def __init__(self):
        pass
        
    @classmethod
    def open(cls, key: str, filename: str) -> TextIOWrapper:
        path = join(LOG_DIR, filename)
        logger = None
        try: 
            logger = open(path, 'a')
        except Exception as e:
            print(e)
        cls.loggers[key]=logger
        return logger

    @classmethod
    def write(cls, key: str, msg: str) -> None:
        try:
            cls.loggers[key].write(msg)
        except KeyError:
            print("[!] Key does not exist.") 
        except Exception as ex:
            print("[!] ")
            
    @classmethod
    def close(cls, key: str):
        cls.loggers[key].close()
            
    @classmethod
    def close_all(cls):
        for k, v in cls.loggers.items():
            v.close()   
        
    @classmethod
    def get_loggers(cls):
        return cls.loggers