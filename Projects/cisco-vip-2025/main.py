# main.py
from topology_builder import NetworkTopologyBuilder

def main():
    print("Starting Cisco Auto Topology Tool...")
    # 1. Create the topology builder
    topology = NetworkTopologyBuilder()
    
    # 2. Point it to your Conf directory
    config_directory = "Conf" 
    
    # 3. Build the topology from the config files!
    topology.build_topology_from_configs(config_directory)
    
    # DEBUG: Show interfaces found on each device
    print("\nDEBUG: Interfaces found on each device:")
    for hostname, device_parser in topology.devices.items():
        print(f"{hostname}:")
        for intf in device_parser.interfaces:
            if intf.get('ip_address'):
                print(f"  - {intf['name']}: {intf['ip_address']}/{intf.get('subnet_mask')} -> Network: {intf.get('network')}")
        print()  # Add empty line between devices
    
    # 4. Print a summary to the console
    topology.print_topology_summary()
    
    # 5. Generate a visual diagram (This will pop up a window and save a file)
    # topology.visualize_topology()  # COMMENTED OUT FOR NOW
    
    print("Done! Check the 'generated_topology.png' file.")

if __name__ == "__main__":
    main()