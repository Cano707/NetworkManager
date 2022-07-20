import re
from typing import List, Union
from ciscoconfparse import CiscoConfParse


#TODO - Check if channel is free to use

#TODO - Is it better to return to the priv. EXEC mode after each method or to check everything...
#       It is better to return to User EXEC mode - because it is possible that the user wants to run 
#       only one command for example. It would be insecure to leave the device in a EXEC mode.
#       ... But also it is possible to logout of the device after the connection has been closed

#TODO - Error message needs to be parsed. All possible errors?

#TODO - Different OS means different cmds. Does each Series only have one OS or can they differ?
class CiscoBaseRouter:
    """base"""
    
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
        """reset_mode"""
        handler.enable()
        if handler.check_config_mode():
            print("EXISING CONFIG MODE")
            handler.exit_config_mode()
        
            
    @classmethod
    def __error_check(cls, res) -> bool:# error_types: List[str]) -> bool:
        res=res.strip()
        error_marker=res[0:2]
        if error_marker[0]=="%" and error_marker[1]==" ":
            return True
        return False
    
    @classmethod
    def __send_config_set(cls, handler, commands) -> str:
        try:
            res=handler.send_config_set(commands)
            return res
        except Exception as e:
            #TODO - Logging
            return False
        
    @classmethod    
    def __send_command(cls, handler, commands: Union[str, list]) -> Union[str, bool]:
        try: 
            if type(commands) is str:
                res=handler.send_command(commands)
            elif type(commands) is list:
                for command in commands:
                    print(f"SENDING {command}")
                    res=handler.send_command(command)
            return res
        except Exception as e:
            #TODO - Logging
            print(e)
            return False
        
    @classmethod
    def __write_channel(cls, handler, commands: Union[str, list]):
        try:
            if type(commands) is str:
                handler.write_channel("\n")
                res=handler.write_channel(commands)
            elif type(commands) is list:
                for command in commands:
                    handler.write_channel("\n")
                    res=handler.write_channel(command)
            return res
        except Exception as e:
            print(e)
            return False
    
    @classmethod
    def show_version(cls, handler):
        """version"""
        command="show version | include Version"
        cls.__reset_mode(handler)
        res=cls.__send_command(handler, command)
        if not res and not cls.__error_check(res):
            return "failed"
        parsed_res=cls.show_version_parser(res)
        return parsed_res

    @staticmethod
    def show_version_parser(data):
        version={}
        version_pattern=r"Version\s*(.*?)(?=,)"
        version_matches=re.search(version_pattern, data)
        if version_matches:
            version={"version": version_matches.groups()[0]}
        return version
    
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
    def show_ipv4_route(cls, handler):
        """ipv4_route"""
        command="show ip route"
        cls.__reset_mode(handler)
        res=cls.__send_command(handler, command)
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
        """interface_ip"""
        commands=[
            f"interface {interface_type}{interface_id}",
            f"ip address {ip} {subnet}"
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
    def configure_interface_description(cls, handler, interface_type, interface_id, description):
        """interface_description"""
        commands=[
            f"interface {interface_type}{interface_id}",
            f"description {description}"
            ]
        cls.__reset_mode(handler)
        res=cls.__send_config_set(handler, commands)
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
    
    """
    @classmethod
    def ssh(cls, handler, domain_name, modulus_bits=1024, ):
        commands=['ip domain-name FH', 
                  'crypto key generate rsa', 
                  {}, 
                  'username {} password {}', 
                  'line vty {} {}', 
                  'login {}', 
                  'transport input ssh', 
                  'exit', 
                  'ip ssh version {}']
    """

        
    
CiscoBaseRouter.MAP = {
    "show": {
        CiscoBaseRouter.show_version.__doc__: {
            "func": CiscoBaseRouter.show_version,
            "info": "",
            "args": list(),
            "opts": list(),
            "db": {"write": False, "field": ""}
        },
        CiscoBaseRouter.show_ipv4_route.__doc__: {
            "func": CiscoBaseRouter.show_ipv4_route,
            "info": "",
            "args": list(),
            "opts": list(), 
            "db": {"write": False, "field": ""}
        },
        CiscoBaseRouter.show_interfaces.__doc__: {
            "func": CiscoBaseRouter.show_interfaces,
            "info": "",
            "args": list(),
            "opts": list(), 
            "db": {"write": False, "field": ""}
        },
        CiscoBaseRouter.show_running_config.__doc__: {
            "func": CiscoBaseRouter.show_running_config,
            "info": "",
            "args": list(),
            "opts": list(), 
            "db": {"write": False, "field": ""}
        }
    },
    "configure": {
        CiscoBaseRouter.configure_interface_ip.__doc__: {
            "func": CiscoBaseRouter.configure_interface_ip,
            "info": "",
            "args": ["interface_type", "interface_id", "ip", "subnet"],
            "opts": list(), 
            "db": {"write": False, "field": ""}
        },
        CiscoBaseRouter.configure_interface_description.__doc__: {
            "func": CiscoBaseRouter.configure_interface_description,
            "info": "",
            "args": ["interface_type", "interface_id", "description"],
            "opts": list(), 
            "db": {"write": False, "field": ""}
        },
        CiscoBaseRouter.configure_shutdown_interface.__doc__:{
            "func": CiscoBaseRouter.configure_shutdown_interface,
            "info": "",
            "args": ["interface_type", "interface_id", "shutdown"],
            "opts": list() , 
            "db": {"write": False, "field": ""}
        },
        CiscoBaseRouter.configure_hostname.__doc__: {
            "func": CiscoBaseRouter.configure_hostname,
            "info": "Reconnect to the device after execution!",
            "args": ["hostname"],
            "opts": list(), 
            "db": {"write": True, "field": "hostname"} 
        }
        
    },
    "general": {
        CiscoBaseRouter.custom_config_command.__doc__: {
            "func" : CiscoBaseRouter.custom_config_command,
            "info": "",
            "args" : list(),
            "opts": list(),
            "db": {"write": False, "field": ""}
        },
        CiscoBaseRouter.copy.__doc__: {
            "func" : CiscoBaseRouter.copy,
            "info": "",
            "args" : ["source", "source_file", "destination", "destination_file"],
            "opts": list(),
            "db": {"write": False, "field": ""}
        },
        CiscoBaseRouter.upload_running_config.__doc__: {
            "func": CiscoBaseRouter.upload_running_config,
            "info": "",
            "args": ["running_config"],
            "opts": list(), 
            "db": {"write": False, "field": ""}
        },
        CiscoBaseRouter.store_running_config_to_database.__doc__: {
            "func": CiscoBaseRouter.store_running_config_to_database,
            "info": "",
            "args": list(),
            "opts": list(),
            "db": {"write": True, "field": "config"}
        }
    }
}