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
    
    """ COMMUNICATION AND EVALUATION FUNCTIONS """
    
    @classmethod
    def __reset_mode(cls, handler) -> None:
        """reset_mode"""    
        handler.enable()
        if handler.check_config_mode():
            handler.exit_config_mode()
            
    @classmethod
    def __error_check(cls, res) -> bool:# error_types: List[str]) -> bool:
        print("__error_check ", res)
        if(not res):
            return True
        res=res.strip()
        error_marker=res[0:2]
        if "%" in error_marker and " " == error_marker[1]:
            return True
        return False
    
    @classmethod
    def __send_config_set(cls, handler, commands):
        res=handler.send_config_set(commands)
        return res
        
    @classmethod
    def send_config_set(cls, handler, commands):
        try:
            cls.__reset_mode(handler)
            print(f"[i] Base Device - send_config_set: {commands=}")
            res=handler.send_config_set(commands)
            if not res or cls.__error_check(res):
                raise
        except Exception as e:
            return False
        return True
        
    @classmethod
    def send_command(cls, handler, command):
        cls.__reset_mode(handler)
        print(f"[i] Base Device - send_command: {command=}")
        res=handler.send_command(command)
        if not res or cls.__error_check(res):
            return False
        return res
        
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
            #print(e)
            return False
    
    """ COMMUNICATION AND EVALUATION FUNCTIONS """
    
    """ SHOW COMMANDS """
    
    @classmethod
    def show_ospf_advertised_routes(cls, handler): 
        """ospf_advertised_router"""
        command = f"show running-config | section router ospf"
        
        res = cls.send_command(handler, command)
        print("##############")
        print(res)
        print("##############")
        if not res:
            return False
        parsed_res = cls.show_ospf_advertised_routes_parser(res)
        return parsed_res
    
    @staticmethod
    def show_ospf_advertised_routes_parser(res):
        ospf_table = {}
        regex = r"network\s+(\d+.\d+.\d+.\d+)\s+(\d+.\d+.\d+.\d+)\s+area\s+(\d+)"
        matches = re.finditer(pattern=regex, string=res, flags=re.MULTILINE)
        for match in matches:
            groups = match.groups()
            network = groups[0]
            wildcard = groups[1]
            area = groups[2]
            ospf_table[network] = {"wildcard": wildcard, "area": area}
        return ospf_table
    
    @classmethod
    def show_hostname(cls, handler) -> str:
        """hostname"""
        command = "show running-config | section hostname"
        res = cls.send_command(handler, command)
        print("RES HOSTNAME ", res)
        if not res:
            return False
        parsed_res = cls.show_hostname_parser(res)
        return parsed_res
    
    @staticmethod
    def show_hostname_parser(data):
        return data.split(" ")[1]
    
    @classmethod
    def show_version(cls, handler):
        """version"""
        command="show version | include Version"
        #print("SHOW VERSION")
        res=cls.send_command(handler, command)
        #print(f"[i] show_version: {res=}")
        if not res:
            return False
        parsed_res=cls.show_version_parser(res)
        return parsed_res

    @staticmethod
    def show_version_parser(data):
        version={}
        version_pattern=r"Version\s*(.*?)(?=,)"
        version_matches=re.search(version_pattern, data)
        version = version_matches.groups()[0] if version_matches else False
        return version
    
    @classmethod
    def show_ipv4_route(cls, handler):
        """ipv4_route"""
        command="show ip route | begin Gateway"
        
        ret=cls.send_command(handler, command)
        parsed_res=cls.show_ipv4_route_parser(ret) if ret else False
        return parsed_res
    
    @staticmethod
    def show_ipv4_route_parser(routingtable_string):
        pattern = r"(Gateway)|(?:^\s*?(\d+\.\d+\.\d+\.\d+\/\d+).*$)|(?:^([A-Za-z]+.*?)\s+([A-Za-z]+.*?)?\s+(\d+\.\d+\.\d+\.\d+(?:\/\d+)?)\s+?(?:(\[\d+\/\d+\]).*?(\d+\.\d+\.\d+\.\d+))?.*?,.*?(?=[A-Za-z0-9])(?:([A-Za-z]*[Ee]thernet\d+(?:\/\d*)*)).*?$)"
        matches = re.finditer(pattern, routingtable_string, re.MULTILINE)
        routing_table = {}
        last_root_network = None
        for match in matches:
            groups = match.groups()
            
            if (groups[0] is not None and "Gateway" in groups[0]):
                continue
            
            if (groups[2] is not None and "S*" in groups[2]):
                routing_table["0.0.0.0/0"] = {"code": "S*", "subcode": "", "metric": "", "next_hop_ip": "", "next_hop_interface": groups[-1]}
                continue
            
            if (groups[1] != None):
                last_root_network = groups[1]
                routing_table[groups[1]] = {}
                continue

            subnetwork = {"code": groups[2], "subcode": groups[3], "metric": groups[5], "next_hop_ip": groups[6], "next_hop_interface": groups[-1]}
            routing_table[last_root_network][groups[4]] = subnetwork
            
        return routing_table
    
    @classmethod
    def show_running_config(cls, handler):
        """running_config"""
        command="show running-config"

        ret=cls.send_command(handler, command)
        res=ret.split("\n") if ret else False
        return res
    
    @classmethod
    def show_interfaces(cls, handler) -> str:
        """interfaces"""
        command="show running-config | begin interface" 

        ret=cls.send_command(handler, command)
        parsed_res=cls.show_interfaces_parser(ret) if ret else False
        return parsed_res
    
    @staticmethod
    def show_interfaces_parser(data):
        data=[s for s in data.splitlines() if s]
        parser=CiscoConfParse(data)
        NUM_PATTERN=r"(\d+(?:(?:[\/?|\.]?)(?:(?<=[\/|\.])\d*\.?\d*)?))"
        INTERFACE_PATTERNS={"ethernet": r"^interface [Ee]thernet", "fastethernet": r"^interface [Ff]ast[Ee]thernet", "gigabitethernet": r"^interface [Gg]igabit[Ee]thernet"}
        result={}
        for interface_type, interface_pattern in INTERFACE_PATTERNS.items():
            interface_result={}
            interface_objs=parser.find_objects(interface_pattern)
            for interface in interface_objs:
                matches=re.search(NUM_PATTERN, interface.text)
                key=matches.groups()[0]
                interface_dict={"ip": "", "subnet": "", "shutdown": True, "encapsulation": {"type": "", "tag": 0, "native": False}}
                shutdown=bool(interface.re_match_iter_typed(r"(shutdown)", default=""))
                ip=interface.re_match_iter_typed(r"ip\s+address\s+(\d+.\d+.\d+.\d+)", default="")
                subnet=interface.re_match_iter_typed(r"ip\s+address\s+\d+.\d+.\d+.\d+\s+(\d+.\d+.\d+.\d+)", default="")
                description=interface.re_match_iter_typed(r"(?<=description)(.*)", default="")
                encapsulation_type=interface.re_match_iter_typed(r"encapsulation\s+(\S+)\s")
                if encapsulation_type:
                    encapsulation_tag=interface.re_match_iter_typed(r"encapsulation\s+\S+\s+(\d+)", result_type=int)
                    encapsulation_native=bool(interface.re_match_iter_typed(r"encapsulation\s+\S+\s+\d+(\S+)", default=False))
                    interface_dict["encapsulation"]= {"type": encapsulation_type, "tag": encapsulation_tag, "native": encapsulation_native}
                interface_dict={**interface_dict, "ip": ip, "subnet": subnet, "shutdown": shutdown, "description": description}
                interface_result[key]=interface_dict
            result[interface_type]=interface_result
        return result
    
    @classmethod
    def show_inventory(cls, handler):
        """inventory"""
        command = "show inventory"
        #print("SHOW INVENTORY")
        ret = cls.send_command(handler, command)
        parsed_res = cls.show_inventory_parser(ret) if ret else False
        return parsed_res
    
    @staticmethod
    def show_inventory_parser(data):
        NAME_PATTERN = r"(?<=NAME:).*?\"(.*?)\""
        DESCR_PATTERN = r"(?<=DESCR:).*?\"(.*?)\""
        PID_PATTERN = r"(?<=PID:).*?\s.*?(\d+)"
        VID_PATTERN = r"(?<=VID:).*?(.*?),"
        SN_PATTERN = r"(?<=SN:).*?(.*)"
        data = [s for s in data.splitlines() if s]
        result = {}
        last_key = None
        for datum in data:
            name_search = re.search(pattern=NAME_PATTERN, string=datum)
            if name_search:
                descr_search = re.search(pattern=DESCR_PATTERN, string=datum)
                name = name_search.groups()[0].strip()
                descr = descr_search.groups()[0].strip()
                result[name] = {"descr": descr}
                last_key = name
            else:
                pid_search = re.search(pattern=PID_PATTERN, string=datum)
                vid_search = re.search(pattern=VID_PATTERN, string=datum)
                sn_search = re.search(pattern=SN_PATTERN, string=datum)
                pid = pid_search.groups()[0].strip()
                vid = vid_search.groups()[0].strip()
                sn = sn_search.groups()[0].strip()           
                result[last_key].update({"pid": pid, "vid": vid, "sn": sn})
        return result    
        
    @classmethod
    def show_ospf(cls, handler):
        """ospf"""
        command = "sh ip ospf"
        res = cls.send_command(handler, command)
        parsed_res = cls.show_ospf_parser(res) if res else False
        return parsed_res
        
    @staticmethod
    def show_ospf_parser(data):
        pattern = r"ospf\s*(\d+).*(\d+.\d+.\d+.\d+)"
        match = re.search(pattern=pattern, string=data)
        result = {"process": "", "id": ""}
        if not match:
            return result
        groups = match.groups()
        result["process"] = groups[0]
        result["id"] = groups[1]
        return result
    
    @classmethod
    def show_default_route(cls, handler):
        """default_route"""
        command = "show ip route"
        res = cls.send_command(handler, command)
        parsed_res = cls.show_default_route_parser(res) if res else False
        return parsed_res
    
    @staticmethod
    def show_default_route_parser(data):
        pattern = r"S\*.*?0\.0\.0\.0\/0\s+.*?,(.*)"
        result = {"interface": ""}
        matches = re.search(pattern, data)
        if not matches:
            return result
        groups = matches.groups()
        result["interface"] = groups[0]
        return result
     
    """ SHOW COMMANDS"""
    
    @classmethod
    def configure_line_vty_ssh_enable(cls, handler, line_from, line_to, password):
        """line_vty_ssh"""
        commands=[
            f"line vty {line_from} {line_to}",
            f"password {password}",
            f"transport input ssh",
            "login"
        ]
        return True if cls.send_config_set(handler, commands) else False
    
    @classmethod
    def configure_interface_description(cls, handler, interface_type, interface_id, description):
        """interface_description"""
        commands=[
            f"interface {interface_type}{interface_id}",
            f"description {description}"
            ]
        return True if cls.send_config_set(handler, commands) else False
     
    @classmethod
    def configure_interface_ip(cls, handler, interface_type, interface_id, ip, subnet):
        """interface_ip"""
        commands=[
            f"interface {interface_type}{interface_id}",
            f"ip address {ip} {subnet}"
            ]
        return True if cls.send_config_set(handler, commands) else False
    
    @classmethod
    def configure_interface_native_vlan(cls, handler, interface_type, interface_id, native_vlan):
        """interface_native_vlan"""
        commands=[
            f"interface {interface_type}{interface_id}",
            f"encapsulation dot1q {native_vlan} native"
            ]
        return True if cls.send_config_set(handler, commands) else False
    
    @classmethod
    def configure_shutdown_interface(cls, handler, interface_type: str, interface_id: str, shutdown: bool):
        """interface_shutdown"""
        commands=[
            f"interface {interface_type}{interface_id}",
            "shutdown" if shutdown else "no shutdown"
        ]
        return True if cls.send_config_set(handler, commands) else False
    
    @classmethod
    def configure_enable_secret(cls, handler, secret):
        """enable_secret"""
        commands=[
            f"enable {secret}"
        ]
        return True if cls.send_config_set(handler, commands) else False
        
    @classmethod
    def configure_hostname(cls, handler, hostname):
        """hostname"""
        commands=[
            f"hostname {hostname}"
        ]
        return True if cls.send_config_set(handler, commands) else False
          
    @classmethod
    def configure_default_route_interface(cls, handler, next_hop_ip_interface):
        """default_route_interface"""
        command = [
            f"ip route 0.0.0.0 0.0.0.0 {next_hop_ip_interface}"
        ]
        return True if cls.send_config_set(handler, command) else False
        
    @classmethod
    def configure_static_route(cls, handler, network, mask, next_hop_ip_interface):
        """static_route"""
        command = [
            f"ip route {network} {mask} {next_hop_ip_interface}"
        ] 
        return True if cls.send_config_set(handler, command) else False
    
    @classmethod
    def configure_delete_static_route(cls, handler, network, mask, next_hop_ip_interface):
        """delete_static_route"""
        command = [
            f"no ip route {network} {mask} {next_hop_ip_interface}"
        ] 
        return True if cls.send_config_set(handler, command) else False
    
    @classmethod
    def configure_enable_ospf(cls, handler, process_id, router_id):
        """enable_ospf"""
        command = [
            f"router ospf {process_id}",
            f"router-id {router_id}"
        ]
        return True if cls.send_config_set(handler, command) else False
    
    @classmethod
    def configure_ospf_network(cls, handler, process_id, network, wildcard, area):
        """ospf_network"""
        command = [
            f"router ospf {process_id}",
            f"network {network} {wildcard} area {area}",
        ]
        return True if cls.send_config_set(handler, command) else False
    
    @classmethod
    def configure_no_ospf_network(cls, handler, process_id, network, wildcard, area):
        """no_ospf_network"""
        command = [
            f"router ospf {process_id}",
            f"no network {network} {wildcard} area {area}",
        ]
        return True if cls.send_config_set(handler, command) else False
    
    @classmethod
    def autodetect(cls, handler) -> List[str]:
        inventory = cls.show_inventory(handler)
        #print(f"inventory: {inventory}")
        pids = [value["pid"] for _, value in inventory.items() if inventory]
        return pids
    
    @classmethod
    def upload_running_config(cls, handler, running_config: List[str]):
        """upload_running_config"""
        return True if cls.send_config_set(handler, running_config) else False
        
    @classmethod
    def copy_running_config_to_startup_config(cls, handler):
        """copy_running_config_to_startup_config"""
        commands = [
            "copy running-config startup-config"
        ]
        return True if cls.send_config_set(handler, commands) else False 
    
    @classmethod
    def custom_config_command(cls, handler, command):
        """custom_config_command"""
        res=cls.__send_config_set(handler, [command])
        if not res and not cls.__error_check(res):
            return False
        return True
    
    @classmethod
    def reset_startup_config(cls, handler):
        """reset_startup_config"""
        commands = [
            "end",
            f"write erase",
            "reload",
            "\n"
        ]
        return True if cls.send_config_set(handler, commands) else False 
    
    
CiscoBaseRouter.MAP = {
    "show": {
        CiscoBaseRouter.show_ospf_advertised_routes.__doc__: {
            "func": CiscoBaseRouter.show_ospf_advertised_routes,
            "info": "",
            "args": list(),
            "opts": list(),
            "db": {"write": True, "update":False, "field": "ospf_routes"}
        },
        CiscoBaseRouter.show_hostname.__doc__: {
            "func": CiscoBaseRouter.show_hostname,
            "info": "",
            "args": list(),
            "opts": list(),
            "db": {"write": True, "update":False, "field": "hostname"}
        },
        CiscoBaseRouter.show_version.__doc__: {
            "func": CiscoBaseRouter.show_version,
            "info": "",
            "args": list(),
            "opts": list(),
            "db": {"write": True, "update":False, "field": "version"}
        },
        CiscoBaseRouter.show_ipv4_route.__doc__: {
            "func": CiscoBaseRouter.show_ipv4_route,
            "info": "",
            "args": list(),
            "opts": list(), 
            "db": {"write": True, "update":False, "field": "ipv4_route"}
        },
        CiscoBaseRouter.show_interfaces.__doc__: {
            "func": CiscoBaseRouter.show_interfaces,
            "info": "",
            "args": list(),
            "opts": list(), 
            "db": {"write": True, "update":False, "field": "interfaces"}
        },
        CiscoBaseRouter.show_running_config.__doc__: {
            "func": CiscoBaseRouter.show_running_config,
            "info": "",
            "args": list(),
            "opts": list(), 
            "db": {"write": True, "update":False, "field": "running_config"}
        },
        CiscoBaseRouter.show_inventory.__doc__: {
            "func": CiscoBaseRouter.show_inventory,
            "info": "",
            "args": list(),
            "opts": list(),
            "db": {"write": True, "update": False, "field": "inventory"}
        },
        CiscoBaseRouter.show_ospf.__doc__: {
            "func": CiscoBaseRouter.show_ospf,
            "info": "",
            "args": list(),
            "opts": list(),
            "db": {"write": True, "update": False, "field": "ospf"}
        },
        CiscoBaseRouter.show_default_route.__doc__: {
            "func": CiscoBaseRouter.show_default_route,
            "info": "",
            "args": list(),
            "opts": list(),
            "db": {"write": True, "update": False, "field": "default_route"}
        }
    },
    "configure": {
        CiscoBaseRouter.configure_enable_secret.__doc__: {
            "func": CiscoBaseRouter.configure_enable_secret,
            "info": "",
            "args": ["secret"],
            "opts": list(),
            "db": {"write": True, "update": True, "callback": CiscoBaseRouter.show_running_config, "field": "running_config"}
        },
        CiscoBaseRouter.configure_line_vty_ssh_enable.__doc__: {
            "func": CiscoBaseRouter.configure_line_vty_ssh_enable,
            "info": "",
            "args": ["line_from", "line_to", "password"],
            "opts": list(),
            "db": {"write": True, "update": True, "callback": CiscoBaseRouter.show_running_config, "field": "running_config"}
        },
        CiscoBaseRouter.configure_interface_ip.__doc__: {
            "func": CiscoBaseRouter.configure_interface_ip,
            "info": "",
            "args": ["interface_type", "interface_id", "ip", "subnet"],
            "opts": list(), 
            "db": {"write": False, "update":True, "callback":CiscoBaseRouter.show_interfaces, "field": "interfaces"}
        },
        CiscoBaseRouter.configure_interface_native_vlan.__doc__: {
            "func": CiscoBaseRouter.configure_interface_native_vlan,
            "info": "",
            "args": ["interface_type", "interface_id", "native_vlan"],
            "opts": list(), 
            "db": {"write": False, "update":True, "callback":CiscoBaseRouter.show_interfaces, "field": "interfaces"}
        },
        CiscoBaseRouter.configure_interface_description.__doc__: {
            "func": CiscoBaseRouter.configure_interface_description,
            "info": "",
            "args": ["interface_type", "interface_id", "description"],
            "opts": list(), 
            "db": {"write": False, "update":True, "callback":CiscoBaseRouter.show_interfaces, "field": "interfaces"}
        },
        CiscoBaseRouter.configure_shutdown_interface.__doc__:{
            "func": CiscoBaseRouter.configure_shutdown_interface,
            "info": "",
            "args": ["interface_type", "interface_id", "shutdown"],
            "opts": list() , 
            "db": {"write": False, "update":True, "callback":CiscoBaseRouter.show_interfaces, "field": "interfaces"}
        },
        CiscoBaseRouter.configure_hostname.__doc__: {
            "func": CiscoBaseRouter.configure_hostname,
            "info": "Reconnect to the device after execution!",
            "args": ["hostname"],
            "opts": list(), 
            "db": {"write": False, "update":True, "callback": CiscoBaseRouter.show_hostname, "field": "hostname"} 
        },
        CiscoBaseRouter.configure_default_route_interface.__doc__: {
            "func": CiscoBaseRouter.configure_default_route_interface,
            "info": "Set a default route",
            "args": ["next_hop_ip_interface"],
            "opts": list(), 
            "db": {"write": False, "update":True, "callback": CiscoBaseRouter.show_default_route, "field": "default_route"} 
        },
        CiscoBaseRouter.configure_static_route.__doc__: {
            "func": CiscoBaseRouter.configure_static_route,
            "info": "Set a static route",
            "args": ["network", "mask", "next_hop_ip_interface"],
            "opts": list(), 
            "db": {"write": False, "update":True, "callback": CiscoBaseRouter.show_ipv4_route, "field": "ipv4_route"} 
        },
        CiscoBaseRouter.configure_delete_static_route.__doc__: {
            "func": CiscoBaseRouter.configure_delete_static_route,
            "info": "Delete a static route",
            "args": ["network", "mask", "next_hop_ip_interface"],
            "opts": list(), 
            "db": {"write": False, "update":True, "callback": CiscoBaseRouter.show_ipv4_route, "field": "ipv4_route"} 
        },
        CiscoBaseRouter.configure_enable_ospf.__doc__: {
            "func": CiscoBaseRouter.configure_enable_ospf,
            "info": "Delete a static route",
            "args": ["process_id", "router_id"],
            "opts": list(), 
            "db": {"write": False, "update":True, "callback": CiscoBaseRouter.show_ospf, "field": "ospf"} 
        },
        CiscoBaseRouter.configure_ospf_network.__doc__: {
            "func": CiscoBaseRouter.configure_ospf_network,
            "info": "Add OSPF network",
            "args": ["process_id", "network", "wildcard", "area"],
            "opts": list(), 
            "db": {"write": False, "update":True, "callback": CiscoBaseRouter.show_ipv4_route, "field": "ipv4_route"} 
        },
        CiscoBaseRouter.configure_no_ospf_network.__doc__: {
            "func": CiscoBaseRouter.configure_no_ospf_network,
            "info": "Delete OSPF network",
            "args": ["process_id", "network", "wildcard", "area"],
            "opts": list(), 
            "db": {"write": False, "update":True, "callback": CiscoBaseRouter.show_ipv4_route, "field": "ipv4_route"} 
        }
    },
    "general": {
        CiscoBaseRouter.custom_config_command.__doc__: {
            "func" : CiscoBaseRouter.custom_config_command,
            "info": "",
            "args" : list(),
            "opts": list(),
            "db": {"write": True, "update":True, "callback": CiscoBaseRouter.show_running_config, "field": "running_config"} 
        },
        CiscoBaseRouter.copy_running_config_to_startup_config.__doc__: {
            "func" : CiscoBaseRouter.copy_running_config_to_startup_config,
            "info": "",
            "args" : [],
            "opts": list(),
            "db": {"write": False, "update":False, "callback": None, "field": None} 
        },
        CiscoBaseRouter.upload_running_config.__doc__: {
            "func": CiscoBaseRouter.upload_running_config,
            "info": "",
            "args": ["running_config"],
            "opts": list(), 
            "db": {"write": True, "update":True, "callback": CiscoBaseRouter.show_running_config, "field": "running_config"} 
        },
        CiscoBaseRouter.reset_startup_config.__doc__: {
            "func": CiscoBaseRouter.reset_startup_config,
            "info": "",
            "args": [],
            "opts": list(), 
            "db": {"write": True, "update":True, "callback": CiscoBaseRouter.show_running_config, "field": "running_config"} 
        }
    }
}