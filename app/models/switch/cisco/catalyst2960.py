from app.models.switch.cisco import CiscoBaseSwitch

class CiscoCatalyst2960(CiscoBaseSwitch):
    """catalyst 2960"""
    
CiscoCatalyst2960.MAP={
    "show": {**CiscoBaseSwitch.MAP["show"]},
    "configure": {**CiscoBaseSwitch.MAP["configure"]},
    "general": {**CiscoBaseSwitch.MAP["general"]}
}
