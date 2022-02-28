#TODO - Yet to implement this.

class CiscoBaseSwitch:
    """basic switch"""
    @staticmethod
    def show_version() -> str:
        """Show version"""
        return "show version"
    
CiscoBaseSwitch.MAP={
    "Show": {
        "Show Version": CiscoBaseSwitch.show_version
    }
}