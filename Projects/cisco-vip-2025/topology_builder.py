import networkx as nx
import matplotlib.pyplot as plt
from config_parser import load_config_from_file
import os

class NetworkTopologyBuilder:
    """
    Builds a hierarchical network topology graph from parsed router configurations.
    Uses subnet matching to automatically discover links between devices.
    """

    def __init__(self):
        # Directed graph: Useful for representing traffic flow (e.g., access -> distribution -> core)
        # Can be converted to undirected for certain analyses.
        self.graph = nx.DiGraph()
        self.devices = {} # Key: hostname, Value: CiscoConfigParser object

    def add_device_from_file(self, file_path):
        """Loads and parses a device config from a file and adds it to the graph."""
        device_parser = load_config_from_file(file_path)
        if device_parser is None:
            return False

        self.devices[device_parser.hostname] = device_parser
        # Add the device itself as a node in the graph, with its parser object as an attribute
        self.graph.add_node(device_parser.hostname, type='router', parser=device_parser)
        print(f"Added device: {device_parser.hostname}")
        return True

    def build_topology_from_configs(self, conf_directory):
        """Reads all config files from a directory and builds the topology."""
        print(f"Loading configurations from {conf_directory}...")
        print(f"DEBUG: Items in Conf directory: {os.listdir(conf_directory)}")  # DEBUG LINE
        for device_dir in os.listdir(conf_directory):
            print(f"DEBUG: Processing item: {device_dir}")  # DEBUG LINE
            config_path = os.path.join(conf_directory, device_dir, 'config.dump')
            print(f"DEBUG: Config path: {config_path}")  # DEBUG LINE
            if os.path.isfile(config_path):
                self.add_device_from_file(config_path)
            else:
                print(f"Skipping {device_dir}, config.dump not found.")

        print("\nDiscovering links based on shared subnets...")
        self._discover_links()
        print("Topology build complete.")

    def _discover_links(self):
        """The core logic: finds interfaces on the same subnet and creates graph edges."""
        # A dictionary to map a subnet (network string) to a list of (device, interface) tuples
        subnet_map = {}

        # Step 1: Populate the subnet map
        for hostname, device_parser in self.devices.items():
            for intf in device_parser.interfaces:
                if intf.get('network'): # Only consider interfaces with a valid IP/subnet
                    subnet = intf['network']
                    device_intf_tuple = (hostname, intf)
                    if subnet not in subnet_map:
                        subnet_map[subnet] = []
                    subnet_map[subnet].append(device_intf_tuple)

        # Step 2: For each subnet, create edges between devices found on it
        for subnet, device_intf_list in subnet_map.items():
            # A subnet with 2+ devices is a shared network (a link)
            if len(device_intf_list) >= 2:
                print(f"  Found shared subnet: {subnet}")
                # Create edges between every pair of devices on this subnet
                # This handles point-to-point links (2 devices) and multi-access networks (>2 devices)
                for i in range(len(device_intf_list)):
                    for j in range(i+1, len(device_intf_list)):
                        device_a, intf_a = device_intf_list[i]
                        device_b, intf_b = device_intf_list[j]

                        # **UNIQUE TWIST: Use description if available, else use interface names for the link label**
                        link_name_a_to_b = f"{intf_a['name']} -> {intf_b['name']}"
                        link_name_b_to_a = f"{intf_b['name']} -> {intf_a['name']}"

                        # Add edges in both directions for an undirected relationship,
                        # but store interface-specific data on each directed edge.
                        self.graph.add_edge(device_a, device_b,
                                            label=link_name_a_to_b,
                                            subnet=subnet,
                                            interface_a=intf_a['name'],
                                            interface_b=intf_b['name'])
                        self.graph.add_edge(device_b, device_a,
                                            label=link_name_b_to_a,
                                            subnet=subnet,
                                            interface_a=intf_b['name'],
                                            interface_b=intf_a['name'])
                        print(f"    Created link: {device_a} <-> {device_b}")

            # **UNIQUE TWIST: Handle "stub" networks (only one device on a subnet)**
            # These are often user VLANs or WAN links to an unseen provider.
            # We can represent them as special nodes for a more complete picture.
            elif len(device_intf_list) == 1:
                device, intf = device_intf_list[0]
                stub_network_name = f"STUB_{subnet.replace('/', '_')}"
                # Add a node for the stub network
                self.graph.add_node(stub_network_name, type='network', subnet=subnet)
                # Add a link from the device to the stub network
                link_name = f"{intf['name']} -> {stub_network_name}"
                self.graph.add_edge(device, stub_network_name,
                                    label=link_name,
                                    subnet=subnet,
                                    interface_a=intf['name'])
                print(f"  Found stub network: {subnet} attached to {device}")

import networkx as nx
# import matplotlib.pyplot as plt  # COMMENTED OUT
from config_parser import load_config_from_file
import os

class NetworkTopologyBuilder:
    """
    Builds a hierarchical network topology graph from parsed router configurations.
    Uses subnet matching to automatically discover links between devices.
    """

    def __init__(self):
        # Directed graph: Useful for representing traffic flow (e.g., access -> distribution -> core)
        # Can be converted to undirected for certain analyses.
        self.graph = nx.DiGraph()
        self.devices = {} # Key: hostname, Value: CiscoConfigParser object

    def add_device_from_file(self, file_path):
        """Loads and parses a device config from a file and adds it to the graph."""
        device_parser = load_config_from_file(file_path)
        if device_parser is None:
            return False

        self.devices[device_parser.hostname] = device_parser
        # Add the device itself as a node in the graph, with its parser object as an attribute
        self.graph.add_node(device_parser.hostname, type='router', parser=device_parser)
        print(f"Added device: {device_parser.hostname}")
        return True

    def build_topology_from_configs(self, conf_directory):
        """Reads all config files from a directory and builds the topology."""
        print(f"Loading configurations from {conf_directory}...")
        print(f"DEBUG: Items in Conf directory: {os.listdir(conf_directory)}")  # DEBUG LINE
        for device_dir in os.listdir(conf_directory):
            print(f"DEBUG: Processing item: {device_dir}")  # DEBUG LINE
            config_path = os.path.join(conf_directory, device_dir, 'config.dump')
            print(f"DEBUG: Config path: {config_path}")  # DEBUG LINE
            if os.path.isfile(config_path):
                self.add_device_from_file(config_path)
            else:
                print(f"Skipping {device_dir}, config.dump not found.")

        print("\nDiscovering links based on shared subnets...")
        self._discover_links()
        print("Topology build complete.")

    def _discover_links(self):
        """The core logic: finds interfaces on the same subnet and creates graph edges."""
        # A dictionary to map a subnet (network string) to a list of (device, interface) tuples
        subnet_map = {}

        # Step 1: Populate the subnet map
        for hostname, device_parser in self.devices.items():
            for intf in device_parser.interfaces:
                if intf.get('network'): # Only consider interfaces with a valid IP/subnet
                    subnet = intf['network']
                    device_intf_tuple = (hostname, intf)
                    if subnet not in subnet_map:
                        subnet_map[subnet] = []
                    subnet_map[subnet].append(device_intf_tuple)

        # Step 2: For each subnet, create edges between devices found on it
        for subnet, device_intf_list in subnet_map.items():
            # A subnet with 2+ devices is a shared network (a link)
            if len(device_intf_list) >= 2:
                print(f"  Found shared subnet: {subnet}")
                # Create edges between every pair of devices on this subnet
                # This handles point-to-point links (2 devices) and multi-access networks (>2 devices)
                for i in range(len(device_intf_list)):
                    for j in range(i+1, len(device_intf_list)):
                        device_a, intf_a = device_intf_list[i]
                        device_b, intf_b = device_intf_list[j]

                        # **UNIQUE TWIST: Use description if available, else use interface names for the link label**
                        link_name_a_to_b = f"{intf_a['name']} -> {intf_b['name']}"
                        link_name_b_to_a = f"{intf_b['name']} -> {intf_a['name']}"

                        # Add edges in both directions for an undirected relationship,
                        # but store interface-specific data on each directed edge.
                        self.graph.add_edge(device_a, device_b,
                                            label=link_name_a_to_b,
                                            subnet=subnet,
                                            interface_a=intf_a['name'],
                                            interface_b=intf_b['name'])
                        self.graph.add_edge(device_b, device_a,
                                            label=link_name_b_to_a,
                                            subnet=subnet,
                                            interface_a=intf_b['name'],
                                            interface_b=intf_a['name'])
                        print(f"    Created link: {device_a} <-> {device_b}")

            # **UNIQUE TWIST: Handle "stub" networks (only one device on a subnet)**
            # These are often user VLANs or WAN links to an unseen provider.
            # We can represent them as special nodes for a more complete picture.
            elif len(device_intf_list) == 1:
                device, intf = device_intf_list[0]
                stub_network_name = f"STUB_{subnet.replace('/', '_')}"
                # Add a node for the stub network
                self.graph.add_node(stub_network_name, type='network', subnet=subnet)
                # Add a link from the device to the stub network
                link_name = f"{intf['name']} -> {stub_network_name}"
                self.graph.add_edge(device, stub_network_name,
                                    label=link_name,
                                    subnet=subnet,
                                    interface_a=intf['name'])
                print(f"  Found stub network: {subnet} attached to {device}")

    
    def visualize_topology(self):
        """Generates a simple visual plot of the topology graph."""
        plt.figure(figsize=(12, 8))

        # Define a layout for the nodes (positions in the plot)
        pos = nx.spring_layout(self.graph, seed=42)  # seed for reproducible layout

        # Separate node types for coloring
        router_nodes = [node for node, attr in self.graph.nodes(data=True) if attr.get('type') == 'router']
        network_nodes = [node for node, attr in self.graph.nodes(data=True) if attr.get('type') == 'network']

        # Draw nodes
        nx.draw_networkx_nodes(self.graph, pos, nodelist=router_nodes, node_color='lightblue', node_size=1000, label='Routers')
        nx.draw_networkx_nodes(self.graph, pos, nodelist=network_nodes, node_color='lightgreen', node_size=800, label='Stub Networks')

        # Draw edges with labels
        edge_labels = nx.get_edge_attributes(self.graph, 'label')
        nx.draw_networkx_edges(self.graph, pos, width=2, alpha=0.7)
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_size=8)

        # Draw node labels
        nx.draw_networkx_labels(self.graph, pos)

        plt.title("Automatically Discovered Network Topology")
        plt.legend()
        plt.axis('off')  # Turn off the axis
        plt.tight_layout()
        plt.savefig("generated_topology.png") # Save the figure
        print("Topology visualization saved as 'generated_topology.png'")
        plt.show()
   

    def print_topology_summary(self):
        """Prints a text-based summary of the topology."""
        print("\n" + "="*50)
        print("TOPOLOGY SUMMARY")
        print("="*50)
        print(f"Number of devices: {len(self.devices)}")
        print(f"Number of nodes in graph: {self.graph.number_of_nodes()}")
        print(f"Number of links in graph: {self.graph.number_of_edges() // 2}") # Divide by 2 for undirected count

        print("\nDevices and their interfaces:")
        for hostname, device_parser in self.devices.items():
            print(f"  {hostname}:")
            for intf in device_parser.interfaces:
                if intf.get('ip_address'):
                    print(f"  - {intf['name']}: {intf['ip_address']} ({intf.get('network', 'N/A')})")