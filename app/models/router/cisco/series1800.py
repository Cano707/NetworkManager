from app.models.router.cisco import CiscoBaseRouter

class Cisco1800Series(CiscoBaseRouter):
    """1800 series"""

Cisco1800Series.MAP = {
    "show": {**CiscoBaseRouter.MAP["show"]},
    "configure": {**CiscoBaseRouter.MAP["configure"]},
    "general": {**CiscoBaseRouter.MAP["general"]}
}