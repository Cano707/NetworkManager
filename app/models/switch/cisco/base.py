import re
from typing import List, Union
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
    
    @classmethod
    def configure_interface_description(cls, handler, interface_type, interface_id, description):
        """interface_description"""
        commands=[
            f"interface {interface_type}{interface_id}", 
            f"description {description}"
        ]
        cls.__reset_mode(handler)
        res=cls.__send_config_set(handler, commands)
        if not res and not cls.__error_check(res):
            return "failed"
        return "succeeded"
    
    @classmethod
    def configure_shutdown_interface(cls, handler, interface_type: str, interface_id: str, shutdown: bool):
        """interface_shutdown"""
        commands=[
            f"interface {interface_type}{interface_id}",
            "shutdown" if shutdown else "no shutdown"
        ]
        cls.__reset_mode(handler)
        res=cls.__send_config_set(handler, commands)
        if not res and not cls.__error_check(res):
            return "failed"
        return "succeeded"
    
    @classmethod
    def configure_switchport_access(cls, handler, interface_type: str, interface_id: str, vlan: str): 
        """switchport_access"""
        commands=[
            f"interface {interface_type}{interface_id}",
            "switchmode mode accesss", 
            f"switchport access vlan {vlan}"
        ]
        cls.__reset_mode(handler)
        res=cls.__send_config_set(handler, commands)
        if not res and not cls.__error_check(res):
            return "failed"
        return "succeeded"
    
    @classmethod
    def configure_switchport_trunk(cls, handler, interface_type: str, interface_id: str, native_vlan: str):
        """switchport_trunk"""
        commands=[
            f"interface {interface_type}{interface_id}",
            "switchmode mode trunk", 
            f"switchport trunk native vlan {native_vlan}"
        ]
        cls.__reset_mode(handler)
        res=cls.__send_config_set(handler, commands)
        if not res and not cls.__error_check(res):
            return "failed"
        return "succeeded"
    
    @classmethod
    def upload_running_config(cls, handler, running_config: List[str]):
        """upload_running_config"""
        cls.__reset_mode(handler)
        res=cls.__send_config_set(handler, running_config)
        if not res and not cls.__error_check(res):
            return "failed"
        return "succeeded"  
    
    @classmethod
    def copy(cls, handler, source: str, source_file: str, destination: str, destination_file: str):
        """copy"""
        """Copy from `source` to `destination`"""
        if source_file=="running-config" or source=="running-config" or source=="startup-config" or source_file=="startup-config":
            source_string=f"{source if source else source_file}"
        else:
            source_string=f"{source}:{source_file}"
        
        if destination_file=="running-config" or destination=="running-config" or destination_file=="startup-config" or destination=="startup-config":
            destionation_string=f"{destination if destination else destination_file}"
        else:
            destionation_string=f"{destination}:{destination_file}"
        
        command=[
            f"copy {source_string} {destionation_string}",
            f"{destination_file}",
            f"n"
            ]
        
        cls.__reset_mode(handler)
        cls.__write_channel(handler, command)
        
        # Error check not needed
        return "success"
    
    @classmethod
    def store_running_config_to_database(cls, handler):
        """store_running_config_to_database"""
        res=cls.show_running_config(handler)
        return res
    
    @classmethod
    def custom_config_command(cls, handler, command):
        """custom_config_command"""
        res=cls.__send_config_set(handler, [command])
        if not res and not cls.__error_check(res):
            return "failed"
        return "succeeded"
    
    @classmethod
    def configure_hostname(cls, handler, hostname):
        """hostname"""
        commands=[
            f"hostname {hostname}"
        ]
        cls.__reset_mode(handler)
        res=cls.__send_config_set(handler, commands)
        if not res and not cls.__error_check(res):
            return "failed"
        return hostname
    
    @classmethod
    def upload_running_config(cls, handler, running_config: List[str]):
        """upload_running_config"""
        cls.__reset_mode(handler)
        res=cls.__send_config_set(handler, running_config)
        if not res and not cls.__error_check(res):
            return "failed"
        return "succeeded"   
    
    @classmethod
    def copy(cls, handler, source: str, source_file: str, destination: str, destination_file: str):
        """copy"""
        """Copy from `source` to `destination`"""
        if source_file=="running-config" or source=="running-config" or source=="startup-config" or source_file=="startup-config":
            source_string=f"{source if source else source_file}"
        else:
            source_string=f"{source}:{source_file}"
        
        if destination_file=="running-config" or destination=="running-config" or destination_file=="startup-config" or destination=="startup-config":
            destionation_string=f"{destination if destination else destination_file}"
        else:
            destionation_string=f"{destination}:{destination_file}"
        
        command=[
            f"copy {source_string} {destionation_string}",
            f"{destination_file}",
            f"n"
            ]
        
        cls.__reset_mode(handler)
        cls.__write_channel(handler, command)
        
        # Error check not needed
        return "success"
    
    @classmethod
    def store_running_config_to_database(cls, handler):
        """store_running_config_to_database"""
        res=cls.show_running_config(handler)
        return res
    
    @classmethod
    def custom_config_command(cls, handler, command):
        """custom_config_command"""
        res=cls.__send_config_set(handler, [command])
        if not res and not cls.__error_check(res):
            return "failed"
        return "succeeded"


#TODO - Show running_config write to db - or not - maybe the user does not want to write to db
CiscoBaseSwitch.MAP={
    "show": {
        CiscoBaseSwitch.show_version.__doc__: {
            "func": CiscoBaseSwitch.show_version,
            "info": "",
            "args": list(),
            "opts": list(),
            "db": {"write": False, "field": ""}
        },
        CiscoBaseSwitch.show_vlans.__doc__: {
            "func": CiscoBaseSwitch.show_vlans,
            "info": "",
            "args": list(),
            "opts": list(),
            "db": {"write": False, "field": ""}
            },
        CiscoBaseSwitch.show_running_config.__doc__: {
            "func": CiscoBaseSwitch.show_running_config,
            "info": "",
            "args": list(),
            "opts": list(),
            "db": {"write": False, "field": ""}
        },
        CiscoBaseSwitch.show_interfaces.__doc__: {
            "func": CiscoBaseSwitch.show_interfaces,
            "info": "",
            "args": list(),
            "opts": list(),
            "db": {"write": False, "field": ""}
        }
    }, 
    "configure": {
        CiscoBaseSwitch.configure_interface_description.__doc__: {
            "func": CiscoBaseSwitch.configure_interface_description,
            "info": "",
            "args": ["interface_type", "interface_id", "description"],
            "opts": list(),
            "db": {"write": False, "field": ""}
        },
        CiscoBaseSwitch.configure_shutdown_interface.doc__: {
            "func": CiscoBaseSwitch.configure_shutdown_interface,
            "info": "",
            "args": ["interface_type", "interface_id", "shutdown"],
            "opts": list(),
            "db": {"write": False, "field": ""}
        },
        CiscoBaseSwitch.configure_switchport_access.__doc__: {
            "func": CiscoBaseSwitch.configure_switchport_access,
            "info": "",
            "args": ["interface_type", "interface_id", "vlan"],
            "opts": list(),
            "db": {"write": False, "field": ""}
        },
        CiscoBaseSwitch.configure_switchport_trunk.__doc__: {
            "func": CiscoBaseSwitch.configure_switchport_trunk,
            "info": "",
            "args": ["interface_type", "interface_id", "native_vlan"],
            "opts": list(),
            "db": {"write": False, "field": ""}
        },
        CiscoBaseSwitch.configure_hostname.__doc__: {
            "func": CiscoBaseSwitch.configure_hostname,
            "info": "Reconnect to the device after execution!",
            "args": ["hostname"],
            "opts": list(), 
            "db": {"write": True, "field": "hostname"} 
        }
    },
    "general": {
        CiscoBaseSwitch.custom_config_command.__doc__: {
            "func" : CiscoBaseSwitch.custom_config_command,
            "info": "",
            "args" : list(),
            "opts": list(),
            "db": {"write": False, "field": ""}
        },
        CiscoBaseSwitch.copy.__doc__: {
            "func" : CiscoBaseSwitch.copy,
            "info": "",
            "args" : ["source", "source_file", "destination", "destination_file"],
            "opts": list(),
            "db": {"write": False, "field": ""}
        },
        CiscoBaseSwitch.upload_running_config.__doc__: {
            "func": CiscoBaseSwitch.upload_running_config,
            "info": "",
            "args": ["running_config"],
            "opts": list(), 
            "db": {"write": False, "field": ""}
        },
        CiscoBaseSwitch.store_running_config_to_database.__doc__: {
            "func": CiscoBaseSwitch.store_running_config_to_database,
            "info": "",
            "args": list(),
            "opts": list(),
            "db": {"write": True, "field": "config"}
        }
    }
}