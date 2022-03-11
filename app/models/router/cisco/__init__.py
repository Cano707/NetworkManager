from app.models.router.cisco.base import CiscoBaseRouter
from app.models.router.cisco.series1800 import Cisco1800Series 

"""
models=[
    CiscoBaseRouter,
    Cisco1800Series
    ]
"""

models={
    CiscoBaseRouter.__doc__: CiscoBaseRouter,
    Cisco1800Series.__doc__: Cisco1800Series
}