import re
import os
from ipaddress import ip_interface, IPv4Network

class CiscoConfigParser:
    def __init__(self, config_text, hostname="Unknown"):
        self.config_text = config_text
        self.hostname = hostname
        self.interfaces = []
        self.static_routes = []
        self.routing_protocols = {}
        self.vlan_info = []

    def parse(self):
        self._parse_hostname()
        self._parse_interfaces()
        self._parse_static_routes()
        self._parse_routing_ospf()

    def _parse_hostname(self):
        print(f"DEBUG: Looking for hostname in config text...")  # ADD THIS LINE
        match = re.search(r'^hostname\s+(\S+)', self.config_text, re.MULTILINE)
        if match:
            print(f"DEBUG: Found hostname: {match.group(1)}")  # ADD THIS LINE
            self.hostname = match.group(1)
        else:
            print(f"DEBUG: No hostname found in config")  # ADD THIS LINE

    def _parse_interfaces(self):
        interface_blocks = re.findall(r'interface\s+(\S+[^\n!]*)(.*?)(?=^!|\Z)', self.config_text, re.MULTILINE | re.DOTALL)
        
        for interface_name, interface_config in interface_blocks:
            intf_dict = {'name': interface_name.strip(), 'ip_address': None, 'subnet_mask': None, 'description': None, 'shutdown': False, 'vlan': None}
            
            if re.search(r'^\s*shutdown', interface_config, re.MULTILINE):
                intf_dict['shutdown'] = True

            ip_match = re.search(r'ip address\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)', interface_config)
            if ip_match:
                ip = ip_match.group(1)
                mask = ip_match.group(2)
                intf_dict['ip_address'] = ip
                intf_dict['subnet_mask'] = mask
                try:
                    network = ip_interface(f"{ip}/{mask}").network
                    intf_dict['network'] = str(network)
                    intf_dict['network_object'] = network
                except ValueError:
                    intf_dict['network'] = None
            
            desc_match = re.search(r'description\s+(.*?)$', interface_config, re.MULTILINE)
            if desc_match:
                intf_dict['description'] = desc_match.group(1).strip()
            
            vlan_match = re.search(r'encapsulation dot1Q\s+(\d+)', interface_config)
            if vlan_match:
                intf_dict['vlan'] = vlan_match.group(1)
            elif interface_name.lower().startswith('vlan'):
                vlan_num_match = re.search(r'vlan(\d+)', interface_name, re.IGNORECASE)
                if vlan_num_match:
                    intf_dict['vlan'] = vlan_num_match.group(1)
            
            self.interfaces.append(intf_dict)

    def _parse_static_routes(self):
        routes = re.findall(r'ip route\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)', self.config_text)
        for network, mask, next_hop in routes:
            self.static_routes.append({
                'network': network,
                'mask': mask,
                'next_hop': next_hop
            })

    def _parse_routing_ospf(self):
        ospf_processes = re.findall(r'router ospf\s+(\d+)(.*?)(?=^!|\Z)', self.config_text, re.MULTILINE | re.DOTALL)
        if ospf_processes:
            self.routing_protocols['ospf'] = []
            for process_id, ospf_config in ospf_processes:
                process_info = {'process_id': process_id, 'networks': []}
                networks = re.findall(r'network\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)\s+area\s+(\d+)', ospf_config)
                for network, wildcard, area in networks:
                    process_info['networks'].append({'network': network, 'wildcard': wildcard, 'area': area})
                self.routing_protocols['ospf'].append(process_info)

# Helper function to load a config file from disk and return a parser object
def load_config_from_file(file_path):
    """Reads a config file and returns a parsed CiscoConfigParser object."""
    try:
        with open(file_path, 'r') as f:
            config_text = f.read()
        # Extract a hostname from the filename as a fallback
        base_name = os.path.basename(file_path)
        print(f"DEBUG: File path: {file_path}")  # ADD THIS
        print(f"DEBUG: Base name: {base_name}")  # ADD THIS
        hostname_guess = os.path.splitext(base_name)[0] # 'R1' from 'R1.config.dump'
        print(f"DEBUG: Hostname guess: {hostname_guess}")  # ADD THIS
        parser = CiscoConfigParser(config_text, hostname_guess)
        parser.parse()
        return parser
    except FileNotFoundError:
        print(f"Error: Config file not found at {file_path}")
        return None

# Test code - only runs if this file is executed directly
if __name__ == "__main__":
    sample_config = """
    hostname R1
    interface GigabitEthernet0/0
     ip address 192.168.1.1 255.255.255.0
    interface GigabitEthernet0/1
     ip address 10.0.0.1 255.255.255.252
    """
    
    test_parser = CiscoConfigParser(sample_config)
    test_parser.parse()
    print(f"Hostname: {test_parser.hostname}")
    for intf in test_parser.interfaces:
        print(f"Interface: {intf}")