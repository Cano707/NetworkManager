from app.models.switch.cisco.base import CiscoBaseSwitch
from app.models.switch.cisco.catalyst2950 import CiscoCatalyst2950

models = [
    CiscoBaseSwitch,
    CiscoCatalyst2950
]