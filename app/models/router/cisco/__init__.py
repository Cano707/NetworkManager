from app.models.router.cisco.base import CiscoBaseRouter
from app.models.router.cisco.series1800 import Cisco1800Series 
from app.models.router.cisco.series2600 import Cisco2600Series
from app.models.router.cisco.cisco2911 import Cisco2911

vendor="cisco"

models={
    CiscoBaseRouter.__doc__: CiscoBaseRouter,
    Cisco1800Series.__doc__: Cisco1800Series,
    Cisco2600Series.__doc__: Cisco2600Series,
    Cisco2911.__doc__: Cisco2911,
}


#TODO Other autodetect markers need to be obtained and added
autodetect={
    Cisco2911.__doc__: {"regex": "2911", "command": "show version"},
}