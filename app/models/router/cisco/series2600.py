from app.models.router.cisco import CiscoBaseRouter

class Cisco2600Series(CiscoBaseRouter):
    """2600 series"""

Cisco2600Series.MAP = {
    "show": {**CiscoBaseRouter.MAP["show"]},
    "configure": {**CiscoBaseRouter.MAP["configure"]},
    "general": {**CiscoBaseRouter.MAP["general"]}
}