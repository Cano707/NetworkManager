import re
from typing import List, Union
#from app.models import CommandError
from ciscoconfparse import CiscoConfParse
import copy

#TODO - Yet to implement this.

class CiscoBaseSwitch:   
    """basic"""
    
    """ COMMUNICATION AND EVALUATION FUNCTIONS """
    
    # CHECKED
    @classmethod
    def __reset_mode(cls, handler) -> None:
        """reset mode"""
        handler.enable()
        if handler.check_config_mode():
            handler.exit_config_mode()
    
    # CHECKED
    @classmethod
    def __error_check(cls, res) -> bool:# error_types: List[str]) -> bool:
        print(f"[i] __error_check: {res=}")
        if(not res):
            return True
        res=res.strip()
        error_marker=res[0:2]
        if "%" in error_marker:
            return True
        return False
            
    # CHECKED
    @classmethod
    def __send_config_set(cls, handler, commands):
        res=handler.send_config_set(commands)
        return res
    
    # CHECKED
    @classmethod
    def send_config_set(cls, handler, commands, error_check = True):
        try:
            cls.__reset_mode(handler)
            print(f"[i] Base Device - send_config_set: {commands=}")
            res=handler.send_config_set(commands)
            if error_check and not res and not cls.__error_check(res):
                raise
        except Exception as e:
            return False
        return True
    
    # CHECKED
    @classmethod
    def send_command(cls, handler, command):
        cls.__reset_mode(handler)
        print(f"[i] Base Device - send_command: {command=}")
        res=handler.send_command(command)
        if not res and not cls.__error_check(res):
            return False
        return res
    
    # CHECKED
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
    
    #TODO CHECK
    @classmethod
    def show_interfaces(cls, handler):
        """interfaces"""
        command="show running-config | begin interface" 
        ret=cls.send_command(handler, command)
        parsed_res=cls.show_interfaces_parser(ret) if ret else False
        return parsed_res
    
    # CHECKED
    @staticmethod
    def show_interfaces_parser(data):
        interfaces = {}
        common_data = {
            "description": None,
            "shutdown": True
        }
        ethernet_interface_result = {
            "port-security": {
                "status": False,
                "learn": "dynamic",
                "violation": None,
                "maximum": None,
                "sticky-macs": [],
                "static-macs": []
            },
            "spanning-tree": {
                "portfast": False,
                "bpduguard": False,
            },
            "nonegotiate": None,
            "mode": None,
            "allowed-vlans": [],
            "native-vlan": None,
            
        }
        vlan_interface_result = {
            "ip": None,
            "subnet": None,
        }
        
        NUM_PATTERN=r"(\d+(?:(?:[\/?|\.]?)(?:(?<=[\/|\.])\d*\.?\d*)?))"
        INTERFACE_PATTERNS={"ethernet": r"^interface [Ee]thernet", "fastethernet": r"^interface [Ff]ast[Ee]thernet", "gigabitethernet": r"^interface [Gg]igabit[Ee]thernet", "vlan": r"interface Vlan"}
        data = [s for s in data.splitlines() if s]
        parser = CiscoConfParse(data)
        
        for interface_type, interface_pattern in INTERFACE_PATTERNS.items():
            interface_result = {}
            interface_id = None
            interface_objs = parser.find_objects(interface_pattern)
            for interface in interface_objs:
                #print(f"[i] Interface: {interface=}")
                interface_id = re.search(NUM_PATTERN, interface.text).groups()[0]
                result = {}
                if interface.is_ethernet_intf:
                    #print("[i] Interface - Ethernet")
                    result = copy.deepcopy(ethernet_interface_result)
                    # port-security status
                    port_security_status = interface.re_search_children(r"switchport port-security\s*$")
                    if port_security_status:
                        result["port-security"]["status"] = True
                    #print(f"[i] Interface - Ethernet: port-security-status = {port_security_status=}")
                    
                    # port-security learn
                    port_security_sticky = interface.re_search_children(r"switchport port-security mac-address sticky\s*$")
                    if port_security_sticky:
                        result["port-security"]["learn"] = "sticky"
                    #print(f"[i] Interface - Ethernet: port-security-sticky = {port_security_sticky=}")
                    
                    # port-security violation  
                    port_security_violation = interface.re_match_iter_typed(r"switchport\s+port-security\s+violation\s+([A-Za-z0-9]+)\s*$")
                    if port_security_violation:
                        result["port-security"]["violation"] = port_security_violation
                    #print(f"[i] Interface - Ethernet: port-security-violation = {port_security_violation=}")
                    
                    # port-security maximum
                    port_security_maximum = interface.re_match_iter_typed(r"switchport\s+port-security\s+maximum\s+(\d+)\s*$")
                    if port_security_maximum:
                        result["port-security"]["maximum"] = port_security_maximum
                    #print(f"[i] Interface - Ethernet: port-security-maximum = {port_security_maximum=}")
                    
                    # port-security static macs  
                    port_security_static_macs_children = interface.re_search_children(r"switchport\s+port-security\s+mac-address\s+([A-Za-z0-9]+\.[A-Za-z0-9]+\.[A-Za-z0-9]+)\s*$")
                    for child in port_security_static_macs_children:
                        result["port-security"]["static-macs"].append(child.re_match(r"switchport\s+port-security\s+mac-address\s+([A-Za-z0-9]+\.[A-Za-z0-9]+\.[A-Za-z0-9]+)\s*$"))
                    #print(f"[i] Interface - Ethernet: port-security-static-macs: {result['port-security']['static-macs']}")
                    
                    # port-security sticky macs  
                    port_security_sticky_macs_children = interface.re_search_children(r"switchport\s+port-security\s+mac-address\s+sticky\s+([A-Za-z0-9]+\.[A-Za-z0-9]+\.[A-Za-z0-9]+)\s*$")
                    for child in port_security_sticky_macs_children:
                        result["port-security"]["sticky-macs"].append(child.re_match(r"switchport\s+port-security\s+mac-address\s+sticky\s+([A-Za-z0-9]+\.[A-Za-z0-9]+\.[A-Za-z0-9]+)\s*$"))
                    #print(f"[i] Interface - Ethernet: port-security-sticky-macs: {result['port-security']['sticky-macs']}")
                    
                    # spanning-tree portfast
                    spanning_tree_portfast = interface.re_search_children(r"spanning-tree\s+portfast\s*$")
                    if spanning_tree_portfast:
                        result["spanning-tree"]["portfast"] = True
                    #print(f"[i] Interface - Ethernet: spanning-tree-portfast: {spanning_tree_portfast}")
                        
                    # spanning-tree bpduguard enable
                    spanning_tree_bpduguard = interface.re_search_children(r"spanning-tree\s+bpduguard\s+enable\s*$")
                    if spanning_tree_bpduguard:
                        result["spanning-tree"]["bpduguard"] = True
                    #print(f"[i] Interface - Ethernet: spanning-tree-bpduguard: {spanning_tree_bpduguard}")
                        
                    result["nonegotiate"] = True if interface.re_match_iter_typed(r"(nonegotiate)") else False
                    result["mode"] = interface.re_match_iter_typed(r"mode\s+(.*)").strip()
                    result["access_vlan"] = interface.re_match_iter_typed(r"switchport\s+access\s+vlan\s+(\d+)")
                    result["allowed-vlans"] = interface.re_match_iter_typed(r"switchport\s+trunk\s+allowed\s+vlan\s+([\d,]+)").split(",")
                    result["native-vlan"] = interface.re_match_iter_typed(r"switchport\s+trunk\s+native\s+vlan\s+(\d+)")
                else:
                    result = copy.deepcopy(vlan_interface_result)
                    result["ip"] = interface.re_match_iter_typed(r"ip\s+address\s+([\d\.]+)\s+([\d\.]+)$").strip()
                    result["subnet"] = interface.re_match_iter_typed(r"ip\s+address\s+([\d\.]+)\s+([\d\.]+)$", group=2).strip()
                    
                common_data["description"] = interface.re_match_iter_typed(r"description\s+(.*)").strip()

                if interface.all_children and (interface.re_match_iter_typed(r"(no\s+shutdown)\s*$") or not interface.re_match_iter_typed(r"(shutdown)\s*$")):
                    common_data["shutdown"] = False
                else:
                    common_data["shutdown"] = True
                    
                interface_result[interface_id] = {**result, **common_data}
                
            interfaces[interface_type] = interface_result
            
        return interfaces
    
    # CHECKED
    @classmethod
    def show_hostname(cls, handler) -> str:
        """hostname"""
        command = "show running-config | include hostname"
        res = cls.send_command(handler, command)
        print("RES HOSTNAME ", res)
        if not res:
            return False
        parsed_res = cls.show_hostname_parser(res)
        return parsed_res
    
    # CHECKED
    @staticmethod
    def show_hostname_parser(data):
        return data.split(" ")[1]
    
    # CHECKED
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
    
    # CHECKED
    @staticmethod
    def show_version_parser(data):
        version={}
        version_pattern=r"Version\s*(.*?)(?=,)"
        version_matches=re.search(version_pattern, data)
        version = version_matches.groups()[0] if version_matches else False
        return version
    
    # CHECKED
    @classmethod
    def show_vlans(cls, handler):
        """vlans"""
        command="show vlan brief"
        res=cls.send_command(handler, command)
        if not res:
            return False
        parsed_res=cls.show_vlans_parser(res)
        return parsed_res
    
    # CHECKED
    @staticmethod
    def show_vlans_parser(data):
        vlan_table={}
        lines = data.splitlines()
        last_vlan = None
        for line in lines:
            if len(line) > 0 and ("VLAN" in line and "Name" in line and "Status" in line and "Ports" in line or line[0] == "-"):
                continue
            vlan_regex = r"^(\d+)\s"
            name_regex = r"^\d+\s+([A-Za-z0-9,\/\-]+)\s"
            status_regex = r"^\d+\s+[A-Za-z0-9,\/\-]+\s+([A-Za-z0-9,\/\-]+)\s"
            port_regex = r"^\d+\s+[A-Za-z0-9,\/\-]+\s+[A-Za-z0-9,\/\-]+\s+([A-Za-z0-9,\/\-\s]+)?"
            port_alone_regex = r"([A-Za-z0-9,\/\-\s]+)"
            vlan_match = re.search(pattern=vlan_regex, string=line)
            port_alone_match = re.search(pattern=port_alone_regex, string=line)
            if vlan_match:
                last_vlan = vlan_match.group(1)
                name_match = re.search(pattern=name_regex, string=line)
                status_match = re.search(pattern=status_regex, string=line)
                port_match = re.search(pattern=port_regex, string=line)
                vlan_table[last_vlan] = {"name": name_match.group(1), "status": status_match.group(1), "ports": port_match.group(1).replace(" ", "").replace("\n", ",").split(",") if port_match.group(1) else []}
            elif port_alone_match:
                vlan_table[last_vlan]["ports"].extend(port_alone_match.group(1).replace(" ", "").replace("\n", ",").split(","))
        return vlan_table
    
    # CHECKED
    @classmethod
    def show_running_config(cls, handler):
        """running_config"""
        command="show running-config"

        ret=cls.send_command(handler, command)
        res=ret.split("\n") if ret else False
        return res
    
    #TODO CHECK
    @classmethod
    def show_inventory(cls, handler):
        """inventory"""
        command = "show inventory"
        ret = cls.send_command(handler, command)
        parsed_res = cls.show_inventory_parser(ret) if ret else False
        return parsed_res
    
    #TODO CHECK
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
      
    #TODO CHECK
    @classmethod
    def show_native_vlan(cls, handler):
        """native_vlan"""
        command = "show interfaces trunk"
        res = cls.send_command(handler, command)
        parsed_res = cls.show_native_vlan_parser(res) if res else False
        return parsed_res
        
    @staticmethod 
    def show_native_vlan_parser(data):
        data = "\n".join(data.strip().split("\n\n")[0].split("\n")[1:]) 
        regex = r"([A-Za-z\/0-9\.]+(?=\s))\s+([A-Za-z\/0-9\.]+(?=\s))\s+([A-Za-z\/0-9\.]+(?=\s))\s+([A-Za-z\/0-9\.]+(?=\s))\s+([A-Za-z\/0-9\.]+)"
        matches = re.finditer(pattern=regex, string=data, flags=re.MULTILINE)
        result = {
            "native_vlan": None,
            "ports": {}
        }
        for match in matches:
            groups = match.groups()
            _ports = {"mode": groups[1], "encapsulation": groups[2], "status": groups[3]}
            result["native_vlan"] = groups[-1]
            result["ports"][groups[0]] = _ports
        return result
      
    """ SHOW COMMANDS"""
    
    """ CONFIGURE COMMANDS """
    
    @classmethod
    def configure_enable_secret(cls, handler, secret):
        """enable_secret"""
        commands=[
            f"enable {secret}"
        ]
        return True if cls.send_config_set(handler, commands) else False
    
    # CHECKED
    @classmethod
    def configure_interface_description(cls, handler, interface_type, interface_id, description):
        """interface_description"""
        commands=[
            f"interface {interface_type}{interface_id}", 
            f"description {description}"
        ]
        return True if cls.send_config_set(handler, commands) else False
    
    # CHECKED
    @classmethod
    def configure_shutdown_interface(cls, handler, interface_type: str, interface_id: str, shutdown: bool):
        """interface_shutdown"""
        commands=[
            f"interface {interface_type}{interface_id}",
            "shutdown" if shutdown else "no shutdown"
        ]
        return True if cls.send_config_set(handler, commands) else False
    
    #TODO CHECK
    @classmethod
    def configure_switchport_access(cls, handler, interface_type: str, interface_id: str): 
        """switchport_access"""
        commands=[
            f"interface {interface_type}{interface_id}",
            "switchport mode access", 
            "no shutdown"
        ]
        return True if cls.send_config_set(handler, commands) else False
    
    #TODO CHECK
    @classmethod
    def configure_no_switchport_access(cls, handler, interface_type: str, interface_id: str): 
        """no_switchport_access"""
        commands=[
            f"interface {interface_type}{interface_id}",
            "no switchport mode access", 
            "no shutdown"
        ]
        return True if cls.send_config_set(handler, commands) else False
    
    #TODO CHECK
    @classmethod
    def configure_switchport_access_vlan(cls, handler, interface_type: str, interface_id: str, vlan: str): 
        """switchport_access_vlan"""
        commands=[
            f"interface {interface_type}{interface_id}",
            f"switchport access vlan {vlan}",
        ]
        return True if cls.send_config_set(handler, commands) else False
        
    #TODO CHECK
    @classmethod
    def configure_no_switchport_access_vlan(cls, handler, interface_type: str, interface_id: str, vlan: str): 
        """no_switchport_access_vlan"""
        commands=[
            f"interface {interface_type}{interface_id}",
            f"no switchport access vlan {vlan}",
        ]
        return True if cls.send_config_set(handler, commands) else False
    
    #TODO Check
    @classmethod
    def configure_switchport_access_range(cls, handler, interface_type: str, interface_range: str, vlan: str):
        """switchport_access_range"""
        commands=[
            f"interface range {interface_type}{interface_range}",
            "switchport mode access", 
            f"switchport access vlan {vlan}",
            "no shutdown"
        ]
        return True if cls.send_config_set(handler, commands) else False
    
    #TODO CHECK
    @classmethod
    def configure_switchport_dynamic(cls, handler, interface_type: str, interface_id: str, negotiation_param: str): 
        """switchport_dynamic"""
        if negotiation_param not in ["auto", "desirable"]: 
            return False
        commands=[
            f"interface {interface_type}{interface_id}",
            f"switchport mode dynamic {negotiation_param}", 
            "no shutdown"
        ]
        return True if cls.send_config_set(handler, commands) else False
    
    # CHECKED
    @classmethod
    def configure_switchport_trunk(cls, handler, interface_type: str, interface_id: str, native_vlan: str):
        """switchport_trunk"""
        commands=[
            f"interface {interface_type}{interface_id}",
            "switchport mode trunk", 
            f"switchport trunk native vlan {native_vlan}",
            "no shutdown"
        ]
        return True if cls.send_config_set(handler, commands) else False
    
    @classmethod
    def configure_switchport_trunk_allowed_vlans(cls, handler, interface_type: str, interface_id: str, allowed_vlans: str):
        """switchport_trunk_allowed_vlans"""
        commands=[
            f"interface {interface_type}{interface_id}",
            f"switchport trunk allowed vlan {allowed_vlans}",
        ]
        return True if cls.send_config_set(handler, commands) else False
     
    # CHECKED
    @classmethod
    def configure_hostname(cls, handler, hostname):
        """hostname"""
        commands=[
            f"hostname {hostname}"
        ]
        return True if cls.send_config_set(handler, commands) else False
    
    #TODO CHECK
    @classmethod
    def configure_new_vlan(cls, handler, vlan_id, vlan_name):
        """new_vlan"""
        commands = [
            f"vlan {vlan_id}",
            f"name {vlan_name}",
            "exit"
        ]
        return True if cls.send_config_set(handler, commands) else False
    
    # CHECKED
    @classmethod
    def configure_management_vlan(cls, handler, vlan_id, vlan_name, ip, mask, interface_type, interface_id):
        """management_vlan"""
        commands = [
            f"vlan {vlan_id}",
            f"name {vlan_name}",
            "exit",
            f"interface vlan{vlan_id}",
            f"ip address {ip} {mask}",
            "no shutdown",
            f"interface {interface_type}{interface_id}",
            f"switchport access vlan {vlan_id}",
            "no shutdown",
            "exit"
        ]
        return True if cls.send_config_set(handler, commands) else False
        
    # CHECKED
    @classmethod
    def configure_default_gateway(cls, handler, ip):
        """default_gateway"""
        commands = [
            f"ip default-gateway {ip}"
        ]
        return True if cls.send_config_set(handler, commands) else False
    
    #TODO CHECK
    @classmethod
    def configure_native_vlan(cls, handler, interface_type: str, interface_id: str, vlan: str): 
        """native_vlan"""
        commands=[
            f"interface {interface_type}{interface_id}",
            f"switchport trunk native vlan {vlan}",
        ]
        return True if cls.send_config_set(handler, commands) else False
        
    # ADD TO MAP
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
    
    """  CONFIGURE  """
    
    """  MISCELLANEOUS  """
    
    @classmethod
    def upload_running_config(cls, handler, running_config: List[str]):
        """upload_running_config"""
        return True if cls.send_config_set(handler, running_config, error_check=False) else False  
    
    @classmethod
    def store_running_config_to_database(cls, handler):
        """store_running_config_to_database"""
        res=cls.show_running_config(handler)
        return res
    
    @classmethod
    def custom_config_command(cls, handler, command):
        """custom_config_command"""
        res=cls.send_config_set(handler, [command])
        if not res and not cls.__error_check(res):
            return False
        return True
    
    @classmethod
    def copy_running_config_to_startup_config(cls, handler):
        """copy_running_config_to_startup_config"""
        commands = [
            "copy running-config startup-config"
        ]
        return True if cls.send_config_set(handler, commands) else False 
    
    @classmethod
    def store_running_config_to_database(cls, handler):
        """store_running_config_to_database"""
        res=cls.show_running_config(handler)
        return res
    
    @classmethod
    def custom_config_command(cls, handler, command):
        """custom_config_command"""
        res=cls.send_config_set(handler, [command])
        if not res and not cls.__error_check(res):
            return False
        return True
    
    @classmethod
    def autodetect(cls, handler) -> List[str]:
        inventory = cls.show_inventory(handler)
        #print(f"inventory: {inventory}")
        pids = [value["pid"] for _, value in inventory.items() if inventory]
        return pids

    @classmethod
    def delete_vlans(cls, handler) -> List[str]:
        """delete_vlans"""
        commands = [
            "delete flash:vlan.dat",
            "reload"
        ]
        return True if cls.send_config_set(handler, commands) else False  

    @classmethod
    def reset_startup_config(cls, handler):
        """reset_startup_config"""
        commands = [
            f"write erase"
            "reload"
        ]
        return True if cls.send_config_set(handler, commands) else False  

    """  MISCELLANEOUS  """


#TODO - Show running_config write to db - or not - maybe the user does not want to write to db
CiscoBaseSwitch.MAP={
    "show": {
        CiscoBaseSwitch.show_hostname.__doc__: {
            "func": CiscoBaseSwitch.show_hostname,
            "info": "",
            "args": list(),
            "opts": list(),
            "db": {"write": True, "update": False, "field": "hostname"}
        },
        CiscoBaseSwitch.show_native_vlan.__doc__: {
            "func": CiscoBaseSwitch.show_native_vlan,
            "info": "",
            "args": list(),
            "opts": list(),
            "db": {"write": True, "update": False, "field": "native_vlan"}
        },
        CiscoBaseSwitch.show_version.__doc__: {
            "func": CiscoBaseSwitch.show_version,
            "info": "",
            "args": list(),
            "opts": list(),
            "db": {"write": True, "update": False, "field": "version"}
        },
        CiscoBaseSwitch.show_vlans.__doc__: {
            "func": CiscoBaseSwitch.show_vlans,
            "info": "",
            "args": list(),
            "opts": list(),
            "db": {"write": True, "update":False, "field": "vlans"}
            },
        CiscoBaseSwitch.show_running_config.__doc__: {
            "func": CiscoBaseSwitch.show_running_config,
            "info": "",
            "args": list(),
            "opts": list(),
            "db": {"write": True, "update": False, "field": "running_config"}
        },
        CiscoBaseSwitch.show_interfaces.__doc__: {
            "func": CiscoBaseSwitch.show_interfaces,
            "info": "",
            "args": list(),
            "opts": list(),
            "db": {"write": True, "update": False, "field": "interfaces"}
        },
        CiscoBaseSwitch.show_inventory.__doc__: {
            "func": CiscoBaseSwitch.show_inventory,
            "info": "",
            "args": list(),
            "opts": list(),
            "db": {"write": True, "update": False, "field": "inventory"}
        }
    }, 
    "configure": {
        CiscoBaseSwitch.configure_line_vty_ssh_enable.__doc__: {
            "func": CiscoBaseSwitch.configure_line_vty_ssh_enable,
            "info": "",
            "args": ["line_from", "line_to", "password"],
            "opts": list(),
            "db": {"write": True, "update": True, "callback": CiscoBaseSwitch.show_interfaces, "field": "interfaces"}
        },
        CiscoBaseSwitch.configure_switchport_dynamic.__doc__: {
            "func": CiscoBaseSwitch.configure_switchport_dynamic,
            "info": "",
            "args": ["interface_type", "interface_id", "vlan", "negotiation_param"],
            "opts": list(),
            "db": {"write": True, "update": True, "callback": CiscoBaseSwitch.show_interfaces, "field": "interfaces"}
        },
        CiscoBaseSwitch.configure_interface_description.__doc__: {
            "func": CiscoBaseSwitch.configure_interface_description,
            "info": "",
            "args": ["interface_type", "interface_id", "description"],
            "opts": list(),
            "db": {"write": True, "update": True, "callback": CiscoBaseSwitch.show_interfaces, "field": "interfaces"}
        },
        CiscoBaseSwitch.configure_shutdown_interface.__doc__: {
            "func": CiscoBaseSwitch.configure_shutdown_interface,
            "info": "",
            "args": ["interface_type", "interface_id", "shutdown"],
            "opts": list(),
            "db": {"write": True, "update": True, "callback": CiscoBaseSwitch.show_interfaces, "field": "interfaces"}
        },
        CiscoBaseSwitch.configure_switchport_access_range.__doc__: {
            "func": CiscoBaseSwitch.configure_switchport_access_range,
            "info": "",
            "args": ["interface_type", "interface_range", "vlan"],
            "opts": list(),
            "db": {"write": True, "update": True, "callback": CiscoBaseSwitch.show_interfaces, "field": "interfaces"}
        },
        CiscoBaseSwitch.configure_switchport_access.__doc__: {
            "func": CiscoBaseSwitch.configure_switchport_access,
            "info": "",
            "args": ["interface_type", "interface_id"],
            "opts": list(),
            "db": {"write": True, "update": True, "callback": CiscoBaseSwitch.show_interfaces, "field": "interfaces"}
        },
        CiscoBaseSwitch.configure_no_switchport_access.__doc__: {
            "func": CiscoBaseSwitch.configure_no_switchport_access,
            "info": "",
            "args": ["interface_type", "interface_id"],
            "opts": list(),
            "db": {"write": True, "update": True, "callback": CiscoBaseSwitch.show_interfaces, "field": "interfaces"}
        },
        CiscoBaseSwitch.configure_switchport_access_vlan.__doc__: {
            "func": CiscoBaseSwitch.configure_switchport_access_vlan,
            "info": "",
            "args": ["interface_type", "interface_id", "vlan"],
            "opts": list(),
            "db": {"write": True, "update": True, "callback": CiscoBaseSwitch.show_interfaces, "field": "interfaces"}
        },
        CiscoBaseSwitch.configure_no_switchport_access_vlan.__doc__: {
            "func": CiscoBaseSwitch.configure_no_switchport_access_vlan,
            "info": "",
            "args": ["interface_type", "interface_id", "vlan"],
            "opts": list(),
            "db": {"write": True, "update": True, "callback": CiscoBaseSwitch.show_interfaces, "field": "interfaces"}
        },
        CiscoBaseSwitch.configure_switchport_dynamic.__doc__: {
            "func": CiscoBaseSwitch.configure_switchport_dynamic,
            "info": "",
            "args": ["interface_type", "interface_id", "negotiation_param"],
            "opts": list(),
            "db": {"write": True, "update": True, "callback": CiscoBaseSwitch.show_interfaces, "field": "interfaces"}
        },
        CiscoBaseSwitch.configure_switchport_trunk.__doc__: {
            "func": CiscoBaseSwitch.configure_switchport_trunk,
            "info": "",
            "args": ["interface_type", "interface_id", "native_vlan"],
            "opts": list(),
            "db": {"write": True, "update": True, "callback": CiscoBaseSwitch.show_interfaces, "field": "interfaces"}
        },
        CiscoBaseSwitch.configure_hostname.__doc__: {
            "func": CiscoBaseSwitch.configure_hostname,
            "info": "Reconnect to the device after execution!",
            "args": ["hostname"],
            "opts": list(), 
            "db": {"write": True,  "update": True, "callback": CiscoBaseSwitch.show_hostname, "field": "hostname"} 
        },
        CiscoBaseSwitch.configure_default_gateway.__doc__: {
            "func": CiscoBaseSwitch.configure_default_gateway,
            "info": "",
            "args": ["ip"],
            "opts": list(), 
            "db": {"write": True,  "update": True, "callback": CiscoBaseSwitch.show_running_config, "field": "running_config"} 
        },#configure_management_vlan(cls, "handler", "vlan_id", "vlan_name", "ip", "mask", "interface_type", "interface_id"):
        CiscoBaseSwitch.configure_management_vlan.__doc__: {
            "func": CiscoBaseSwitch.configure_management_vlan,
            "info": "",
            "args": ["vlan_id", "vlan_name", "ip", "mask", "interface_type", "interface_id"],
            "opts": list(), 
            "db": {"write": True,  "update": True, "callback": CiscoBaseSwitch.show_running_config, "field": "running_config"}
        },
        CiscoBaseSwitch.configure_native_vlan.__doc__: {
            "func": CiscoBaseSwitch.configure_native_vlan,
            "info": "",
            "args": ["interface_type", "interface_id", "vlan"],
            "opts": list(), 
            "db": {"write": True,  "update": True, "callback": CiscoBaseSwitch.show_interfaces, "field": "interfaces"}
        },
        CiscoBaseSwitch.configure_new_vlan.__doc__: {
            "func": CiscoBaseSwitch.configure_new_vlan,
            "info": "",
            "args": ["vlan_id", "vlan_name"],
            "opts": list(), 
            "db": {"write": True,  "update": True, "callback": CiscoBaseSwitch.show_vlans, "field": "vlans"}
        },
        CiscoBaseSwitch.configure_switchport_trunk_allowed_vlans.__doc__: {
            "func": CiscoBaseSwitch.configure_switchport_trunk_allowed_vlans,
            "info": "",
            "args": ["interface_type", "interface_id", "allowed_vlans"],
            "opts": list(), 
            "db": {"write": True,  "update": True, "callback": CiscoBaseSwitch.show_interfaces, "field": "interfaces"}
        },
        CiscoBaseSwitch.configure_enable_secret.__doc__: {
            "func": CiscoBaseSwitch.configure_enable_secret,
            "info": "",
            "args": ["secret"],
            "opts": list(), 
            "db": {"write": True,  "update": True, "callback": CiscoBaseSwitch.show_running_config, "field": "running_config"}
        }
    },
    "general": {
        CiscoBaseSwitch.delete_vlans.__doc__: {
            "func" : CiscoBaseSwitch.delete_vlans,
            "info": "",
            "args" : list(),
            "opts": list(),
            "db": {"write": True, "update":True, "callback": CiscoBaseSwitch.show_vlans, "field": "vlans"} 
        },
        CiscoBaseSwitch.custom_config_command.__doc__: {
            "func" : CiscoBaseSwitch.custom_config_command,
            "info": "",
            "args" : list(),
            "opts": list(),
            "db": {"write": True, "update":True, "callback": CiscoBaseSwitch.show_running_config, "field": "running_config"} 
        },
        CiscoBaseSwitch.copy_running_config_to_startup_config.__doc__: {
            "func" : CiscoBaseSwitch.copy_running_config_to_startup_config,
            "info": "",
            "args" : [],
            "opts": list(),
            "db": {"write": False, "update":False, "callback": None, "field": None} 
        },
        CiscoBaseSwitch.upload_running_config.__doc__: {
            "func": CiscoBaseSwitch.upload_running_config,
            "info": "",
            "args": ["running_config"],
            "opts": list(), 
            "db": {"write": True, "update":True, "callback": CiscoBaseSwitch.show_running_config, "field": "running_config"} 
        },
        CiscoBaseSwitch.reset_startup_config.__doc__: {
            "func": CiscoBaseSwitch.reset_startup_config,
            "info": "",
            "args": [],
            "opts": list(), 
            "db": {"write": True, "update":True, "callback": CiscoBaseSwitch.show_running_config, "field": "running_config"} 
        }
    }
}