from app.models.switch.cisco.base import CiscoBaseSwitch
from app.models.switch.cisco.catalyst2950 import CiscoCatalyst2950
from app.models.switch.cisco.catalyst2960 import CiscoCatalyst2960

vendor="cisco"

models = {
    CiscoBaseSwitch.__doc__: CiscoBaseSwitch,
    CiscoCatalyst2950.__doc__: CiscoCatalyst2950,
    CiscoCatalyst2960.__doc__: CiscoCatalyst2960
}



#TODO Other autodetect markers need to be obtained and added
autodetect={
    CiscoCatalyst2960.__doc__: "2960",
}