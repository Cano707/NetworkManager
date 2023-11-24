from app.models.router.cisco import CiscoBaseRouter

class Cisco2911(CiscoBaseRouter):
    """2911"""

Cisco2911.MAP = {
    "show": {**CiscoBaseRouter.MAP["show"]},
    "configure": {**CiscoBaseRouter.MAP["configure"]},
    "general": {**CiscoBaseRouter.MAP["general"]}
}

