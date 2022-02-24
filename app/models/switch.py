class CiscoBaseSwitch:
    @staticmethod
    def show_version() -> str:
        """Show version"""
        return "show version"
    
class CiscoCatalyst2950(CiscoBaseSwitch):
    @staticmethod
    def show_running_config() -> str:
        return "show running-config"
    
CiscoBaseSwitch.MAP={
    "Show": {
        "Show Version": CiscoBaseSwitch.show_version
    }
}
    
CiscoCatalyst2950.MAP={
    "Show": {
        **CiscoBaseSwitch.MAP["Show"], 
       "Show Running-Config": CiscoCatalyst2950.show_running_config
    }
}
