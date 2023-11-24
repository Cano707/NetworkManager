from app.models.switch.cisco import CiscoBaseSwitch

class CiscoCatalyst2950(CiscoBaseSwitch):
    """catalyst 2950"""
    
CiscoCatalyst2950.MAP={
    "show": {**CiscoBaseSwitch.MAP["show"]},
    "configure": {**CiscoBaseSwitch.MAP["configure"]},
    "general": {**CiscoBaseSwitch.MAP["general"]}
}
