import re
from typing import List
#from app.models import CommandError
from ciscoconfparse import CiscoConfParse

#TODO - Yet to implement this.

class CiscoBaseSwitch:
    """basic"""
    
    """
    COMMON_ERRORS=["Invalid input detected at '^' marker."]
    
    VLAN_ERRORS=["No Virtual LANs configured."]
    
    error_map={
        "common": COMMON_ERRORS,
        "vlan": VLAN_ERRORS
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
    def show_vlans(cls, handler):
        command="show vlan brief"
        cls.__reset_mode(handler)
        res=cls.send_command(command)
        if not res and not cls.__error_check(res):
            return "failed"
        parsed_res=cls.show_vlans_parser(res)
        return parsed_res
    
    @staticmethod
    def show_vlans_parser(data):
        root_pattern=r"(?:(\d+)\s+(.*?[^\s]+))\s+(.*?[^\s]+)\s*(.*)"
        sub_pattern=r"(.*)"
        vlan_table=dict()
        root_vlan=None
        for line in data.split("\n"):
            if line:
                if line[0].isnumeric():
                    matches=re.finditer(root_pattern, line.strip())
                    for _, match in enumerate(matches):
                        groups=match.groups()
                        vlan=groups[0]
                        name=groups[1]
                        status=groups[2]
                        ports=[port.strip() for port in groups[3].split(",") if port]
                        root_vlan=vlan
                        vlan_table[vlan]={"name": name, "status": status, "ports": ports}
                elif line[0].isspace():
                    matches=re.finditer(sub_pattern, line.strip())
                    for _, match in enumerate(matches):
                        groups=match.groups()
                        ports=[port.strip() for port in groups[0].split(",") if port]
                        vlan_table[root_vlan]["ports"].extend(ports)
        return vlan_table
    
    @classmethod
    def show_running_config(cls, handler):
        """running_config"""
        command="show running-config"
        cls.__reset_mode(handler)
        res=cls.__send_command(handler, command)
        if not res and not cls.__error_check(res):
            #TODO - Log
            return "failed"
        res=res.split("\n")
        return res
    
    @classmethod
    def show_interfaces(cls, handler):
        """interfaces"""
        command="show running-config | begin interface" 
        cls.__reset_mode(handler)  
        res=cls.__send_command(handler, command)
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
        ALLOWED_VLAN_PATTERN=r"(?:(\d+(?:\-\d*)?))+"
        result={}
        for interface_type, interface_pattern in INTERFACE_PATTERNS.items():
            interface_result=dict()
            interface_objs=parser.find_objects(interface_pattern)
            for interface in interface_objs:
                matches=re.search(NUM_PATTERN, interface.text)
                key=matches.groups()[0]
                interface_dict={"description": "", "switchport": None}
                description=interface.re_match_iter_typed(r"description\s+(\w+)", default="")
                interface_dict["description"]=description
                switchport_mode=interface.re_match_iter_typed(r"switchport\s+mode\s+(\w+)", default="")
                if switchport_mode=="access":
                    vlan=interface.re_match_iter_typed(r"switchport\s+access\s+vlan\s+(\d+)", default="")
                    switchport_dict={"mode": switchport_mode, "vlan": vlan}
                    interface_dict["switchport"]=switchport_dict
                if switchport_mode=="trunk":
                    native_vlan=interface.re_match_iter_typed(r"switchport\s+trunk\s+native\s+vlan\s+(\d+)", default="")
                    allowed_vlans_line=interface.re_match_iter_typed(r"(switchport\s+trunk\s+allowed\s+vlan\s+.*)", default="")
                    allowed_vlans=list()
                    if allowed_vlans_line:
                        allowed_vlans=re.findall(ALLOWED_VLAN_PATTERN, allowed_vlans_line)
                    switchport_dict={"mode": "trunk", "native_vlan": native_vlan, "allowed_vlans": ",".join(allowed_vlans)}
                    interface_dict["switchport"]=switchport_dict
                interface_result[key]=interface_dict
            result[interface_type]=interface_result
        return result
    

    
CiscoBaseSwitch.MAP={
    "show": {
        CiscoBaseSwitch.show_version.__doc__: {
            "func": CiscoBaseSwitch.show_version,
            "args": list(),
            "opts": list()
        },
        CiscoBaseSwitch.show_vlans.__doc__: {
            "func": CiscoBaseSwitch.show_vlans,
            "args": list(),
            "opts": list()
            }
    }
}