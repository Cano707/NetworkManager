import re
from typing import List
from ciscoconfparse import CiscoConfParse


#TODO - Check if channel is free to use

#TODO - Is it better to return to the priv. EXEC mode after each method or to check everything...
#       It is better to return to User EXEC mode - because it is possible that the user wants to run 
#       only one command for example. It would be insecure to leave the device in a EXEC mode.
#       ... But also it is possible to logout of the device after the connection has been closed

#TODO - Error message needs to be parsed. All possible errors?

#TODO - Different OS means different cmds. Does each Series only have one OS or can they differ?
class CiscoBaseRouter:
    """basic router"""
    
    """
    COMMON_ERRORS=["Invalid input detected at '^' marker."]
    
    INTERFACE_ERRORS=["overlaps with"]
    
    error_map={
        "common": COMMON_ERRORS,
        "interface": INTERFACE_ERRORS
    }
    """
    
    @classmethod
    def __reset_mode(cls, handler) -> None:
        """reset mode"""
        if handler.check_config_mode():
            handler.exit_config_mode()
        elif not handler.check_enable_mode():
            handler.enable()
            
    @classmethod
    def __error_check(cls, res) -> bool:# error_types: List[str]) -> bool:
        res=res.strip()
        error_marker=res[0:1]
        if error_marker[0]=="%" and error_marker[1]==" ":
            return True
        return False
        """
        for error_type in error_types:
            if error_type not in cls.error_map:
                raise KeyError(f"error_type {error_type} not found.")
            for error in cls.error_map[error_type]:
                if error in res:
                    #TODO - Logging
                    return True
        return False
        """
    
            
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
        if not res and not cls.__error_check(res):
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
    def show_ipv4_route(cls, handler):
        """show_ip_route"""
        command="show ip route"
        cls.__reset_mode(handler)
        res=cls.__send_command(command)
        if not res and not cls.__error_check(res):
            return "failed"
        parsed_res=cls.show_ipv4_route_parser(res)
        return parsed_res
        
    @staticmethod
    def show_ipv4_route_parser(data):
        routing_table=dict()
        pattern=r"(?:(^[A-Z0-9]+)(?=\s)\s+(?:([A-Z0-9]+)(?=\s))?\s+)?(\d+\.\d+\.\d+\.\d+/\d+)\s+(?:(\[.*\])\s+[A-Za-z]+\s+(\d+\.\d+\.\d+\.\d+))?.*,\s+([A-Za-z]+.*)?"
        matches=re.finditer(pattern, data, re.MULTILINE)
        root_net=None
        for match in matches:
            groups=match.groups()
            groups=[group if group is not None else "" for group in groups]
            if groups[0] != "":
                routing_table[root_net].update({groups[2]: {"code": groups[0], "subcode": groups[1], "metric": groups[3], "next_hop_ip": groups[4], "next_hop_interface": groups[5]}})
            else:
                root_net=groups[2]
                routing_table[root_net]=dict()
        return routing_table
    
    @classmethod
    def show_interfaces(cls, handler) -> str:
        """show_interfaces"""
        command="show running-config | begin interface" 
        cls.__reset_mode(handler)  
        res=cls.__send_command(command)
        if not res and not cls.__error_check(res):
            return "failed"
        parsed_res=cls.show_interfaces_parser(res)
        return parsed_res
    
    @staticmethod
    def show_interfaces_parser(data):
        data=[s for s in data.splitlines() if s]
        parser=CiscoConfParse(data)
        NUM_PATTERN=r"(\d+(?:(?:[\/?|\.]?)(?:(?<=[\/|\.])\d*\.?\d*)?))"
        INTERFACE_PATTERNS={"ethernet": r"^interface [Ee]thernet", "fastthernet": r"^interface [Ff]ast[Ee]thernet", "gigabitethernet": r"^interface [Gg]igabit[Ee]thernet"}
        result={}
        for interface_type, interface_pattern in INTERFACE_PATTERNS.items():
            interface_result=dict()
            interface_objs=parser.find_objects(interface_pattern)
            for interface in interface_objs:
                matches=re.search(NUM_PATTERN, interface.text)
                key=matches.groups()[0]
                interface_dict={"ip": "", "subnet": "", "shutdown": True, "encapsulation": {"type": "", "tag": 0, "native": False}}
                shutdown=bool(interface.re_match_iter_typed(r"(shutdown)", default=""))
                ip=interface.re_match_iter_typed(r"ip\s+address\s+(\d+.\d+.\d+.\d+)", default="")
                subnet=interface.re_match_iter_typed(r"ip\s+address\s+\d+.\d+.\d+.\d+\s+(\d+.\d+.\d+.\d+)", default="")
                encapsulation_type=interface.re_match_iter_typed(r"encapsulation\s+(\S+)\s")
                if encapsulation_type:
                    encapsulation_tag=interface.re_match_iter_typed(r"encapsulation\s+\S+\s+(\d+)", result_type=int)
                    encapsulation_native=bool(interface.re_match_iter_typed(r"encapsulation\s+\S+\s+\d+(\S+)", default=False))
                    interface_dict["encapsulation"]= {"type": encapsulation_type, "tag": encapsulation_tag, "native": encapsulation_native}
                interface_dict={**interface_dict, "ip": ip, "subnet": subnet, "shutdown": shutdown}
                interface_result[key]=interface_dict
            result[interface_type]=interface_result
        return result
    
    @classmethod
    def configure_interface_ip(cls, handler, interface_type, interface_id, ip, subnet):
        """interface"""
        commands=[
            f"interface {interface_type}{interface_id}",
            f"ip address {ip} {subnet}"
            ]
        cls.__reset_mode(handler)
        res=cls.__send_config_set(commands)
        if not res and not cls.__error_check(res):
            return "failed"
        return "succeeded"
    
    @classmethod
    def configure_shutdown_interface(cls, handler, interface_type, interface_id, shutdown):
        """interface_shutdown"""
        commands=[
            f"interface {interface_type}{interface_id}",
            "shutdown" if shutdown else "no shutdown"
        ]
        cls.__reset_mode(handler)
        res=cls.__send_config_set(commands)
        if not res and not cls.__error_check(res):
            return "failed"
        return "succeeded"
    
    @classmethod
    def configure_interface_description(cls, handler, interface_type, interface_id, description):
        """interface_description"""
        commands=[
            f"interface {interface_type}{interface_id}",
            f"description {description}"
            ]
        cls.__reset_mode(handler)
        res=cls.__send_config_set(commands)
        if not res and not cls.__error_check(res): # and not cls.__error_check
            return "failed"
        return "succeeded"
        
    @classmethod
    def configure_hostname(cls, handler, hostname):
        """hostname"""
        commands=[
            f"hostname {hostname}"
        ]
        cls.__reset_mode(handler)
        res=cls.__send_config_set(commands)
        if not res: # and not cls.__error_check
            return "failed"
        return "succeeded"
    
CiscoBaseRouter.MAP = {
    "show": {
        CiscoBaseRouter.show_version.__doc__: {
            "func": CiscoBaseRouter.show_version,
            "args": list(),
            "opts": list()
        },
        CiscoBaseRouter.show_ipv4_route.__doc__: {
            "func": CiscoBaseRouter.show_ipv4_route,
            "args": list(),
            "opts": list()
        },
        CiscoBaseRouter.show_interfaces.__doc__: {
            "func": CiscoBaseRouter.show_interfaces,
            "args": list(),
            "opts": list()
        }
    },
    "configure": {
        CiscoBaseRouter.configure_interface_ip.__doc__: {
            "func": CiscoBaseRouter.configure_interface_ip,
            "args": ["interface_type", "interface_id", "ip", "subnet"],
            "opts": list()
        },
        CiscoBaseRouter.configure_interface_description.__doc__: {
            "func": CiscoBaseRouter.configure_interface_ip,
            "args": ["interface_type", "interface_id", "description"],
            "opts": list()
        },
        CiscoBaseRouter.configure_shutdown_interface.__doc__:{
            "func": CiscoBaseRouter.configure_shutdown_interface,
            "args": ["interface_type", "interface_id", "shutdown"],
            "opts": list() 
        }
        
    }
}