from pydantic import BaseModel
from typing import Optional, Union, Literal
from enum import Enum

class ConnectionType(str, Enum):
    ssh="ssh"
    telnet="telnet"
    serial="serial"

