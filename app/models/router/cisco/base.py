import re
from ciscoconfparse import CiscoConfParse


#TODO - Check if channel is free to use

#TODO - Is it better to return to the priv. EXEC mode after each method or to check everything...
#       It is better to return to User EXEC mode - because it is possible that the user wants to run 
#       only one command for example. It would be insecure to leave the device in a EXEC mode.
#       ... But also it is possible to logout of the device after the connection has been closed

#TODO - Error message needs to be parsed. All possible errors?

#TODO - Instances of classes should be possible - e.g. the state of "enable" needs to be tracked
#       Solved with if statements. 

#TODO - Different OS means different cmds. Does each Series only have one OS or can they differ?
class CiscoBaseRouter:
    """basic router"""
    @staticmethod
    def show_version(handler):
        """show_version"""
        command="show version"
        if handler.check_enable_mode():
            if handler.check_config_mode():
                command="do show version"
        res=handler.send_command(command)
        parsed_res=CiscoBaseRouter.show_version_parser(res)
        return parsed_res

    @staticmethod
    def show_version_parser(data):
        version={}
        uptime={}
        version_pattern=r"Cisco.*?Version\s*(.*?)(?=,)"
        version_matches=re.search(version_pattern, data)
        if version_matches:
            version={"version": version_matches.groups()[0]}
        uptime_pattern=r"(\d*)(?:\s*hours),\s(\d*)"
        uptime_matches=re.search(uptime_pattern, data)
        if uptime_matches:
            uptime={"hour": uptime_matches.groups()[0], "minute": uptime_matches.groups()[1]}
        return {"uptime": uptime, **version}
    
    @staticmethod
    def show_ipv4_route(handler):
        """show_ip_route"""
        command="show ip route"
        if handler.check_enable_mode():
            if handler.check_config_mode():
                command="do show ip route"
        handler.enable()
        res=handler.send_command(command)
        parsed_res=CiscoBaseRouter.show_ipv4_route_parser(res)
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
    
    #TODO - currently only the interfaces are parsed. Future version shall also parse all other params.
    @staticmethod
    def show_interfaces(handler) -> str:
        """show_interfaces"""
        """
        "show run interface ..." to check a particular interface "show run | begin <word>" to start displaying the config at a specific line containing <word> "show run | include <word>" to display all the lines containing the given <word> "show run | section <word>" is a good one, too 
        """
        command="show running-config" # show running-config | interfaces  
        if handler.check_enable_mode():
            if handler.check_config_mode():
                command="do show ip route"
        else:
            handler.enable()    
        res=handler.send_command(command)
        parsed_res=CiscoBaseRouter.show_interfaces_parser(res)
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
    
    @staticmethod
    def configure_interface_ip(handler, interface_type, interface_id, ip, subnet):
        """configure_interface"""
        commands=[
            f"interface {interface_type}{interface_id}",
            f"ip address {ip} {subnet}"
            ]
        res=list()
        if not handler.check_enable_mode():
            handler.enable()
        if handler.check_config_mode():
            handler.exit_config_mode()
        res=handler.send_config_set(commands)
        print(res)
        return res
    
    @staticmethod
    def no_shutdown_interface(handler, interface_type, interface_id):
        pass
    
CiscoBaseRouter.MAP = {
    "show": {
        CiscoBaseRouter.show_version.__doc__: {
            "func": CiscoBaseRouter.show_version,
        },
        CiscoBaseRouter.show_ipv4_route.__doc__: {
            "func": CiscoBaseRouter.show_ipv4_route,
        },
        CiscoBaseRouter.show_interfaces.__doc__: {
            "func": CiscoBaseRouter.show_interfaces,
        }
    },
    "configure": {
        CiscoBaseRouter.configure_interface_ip.__doc__: {
            "func": CiscoBaseRouter.configure_interface_ip,
            "args": ["interface_type", "interface_id", "ip", "subnet"],
            "opt": []
        }
    }
}