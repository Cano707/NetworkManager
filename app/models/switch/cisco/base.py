#TODO - Yet to implement this.

class CiscoBaseSwitch:
    """basic switch"""
    @classmethod
    def __reset_mode(cls, handler) -> None:
        """reset mode"""
        if handler.check_config_mode():
            handler.exit_config_mode()
        elif not handler.check_enable_mode():
            handler.enable()
    
    @classmethod
    def __error_check(cls, res) -> bool:
        pass
            
    @classmethod
    def __send_config_set(cls, handler, commands) -> str:
        try:
            res=handler.send_config_set(commands)
            return res
        except Exception as e:
            #TODO - Logging
            return False
        
    @classmethod    
    def __send_command(cls, handler, command) -> str:
        try: 
            res=handler.send_command(command)
            return res
        except Exception as e:
            #TODO - Logging
            return False
    
    @classmethod
    def show_version(cls, handler):
        """show_version"""
        command="show version"
        cls.__reset_mode(handler)
        res=cls.__send_command(handler, command)
        if not res:
            return "failed"
        parsed_res=cls.show_version_parser(res)
        return parsed_res
    
    @staticmethod
    def show_version_parser(data):
        version={}
        version_pattern=r"Cisco.*?Version\s*(.*?)(?=,)"
        version_matches=re.search(version_pattern, data)
        if version_matches:
            version={"version": version_matches.groups()[0]}
        return version
    
    @classmethod
    def show_vlans(cls, handler):
        command="show vlan"
        cls.__reset_mode(handler)
        res=cls.send_command(command)
        if not res:
            return "failed"
        parsed_res=cls.show_vlans_parser(res)
        return parsed_res
    
    @staticmethod
    def show_vlans_parser(data):
    pass
    
CiscoBaseSwitch.MAP={
    "Show": {
        "Show Version": CiscoBaseSwitch.show_version
    }
}