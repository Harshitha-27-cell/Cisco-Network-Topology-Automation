# Network Topology Discovery Tool – Cisco Internship 2025

## 1. Introduction

This document outlines a Python-based solution developed to automatically analyze Cisco router configurations and build a live, visualized topology of a given network. The tool uses configuration parsing and graph-based discovery to identify inter-device connectivity, IP addressing, and network segmentation.

This system was built with modularity in mind, using:
- Custom configuration parser
- Automated topology builder
- Visual graph generation using NetworkX

The solution supports hierarchical networks with Routers, Switches, Servers, and Endpoints.

## 2. Network Topology Analysis

The tool reads a directory of Cisco router configuration files (e.g., `config.dump`) and extracts interfaces, IP subnets, static routes, OSPF configurations, and VLAN data. Based on IP subnets, the tool:
- Maps shared links between routers/switches
- Identifies stub networks
- Differentiates between device types (router vs. access network)

**Detected Topology Structure:**
- Multiple routers connected via point-to-point subnets
- Stub networks representing server segments or WAN uplinks
- Hierarchical links between core/distribution/edge routers

All topology discovery is data-driven—no manual diagramming needed.

## 3. VLAN and IP Addressing Plan

The tool extracts interface configurations, VLAN IDs (via encapsulation dot1Q or interface naming), and builds a map of all assigned subnets.

Below is a sample output format for detected VLANs and networks:

| VLAN | Name/Type | Subnet          | Device Interface     |
|------|-----------|-----------------|----------------------|
| 10   | Admin     | 192.168.10.0/24 | R1: Gig0/1          |
| 20   | Faculty   | 192.168.20.0/24 | R2: Gig0/2          |
| -    | P2P Link  | 10.0.0.0/30     | R1 ↔ R2 (Gig0/0 ↔ Gig0/0) |
| -    | Server Net| 192.168.40.0/24 | R3: VLAN40 (SVI)    |

This data is auto-inferred from configuration files by matching:
- IP addresses + subnet masks
- VLAN interface naming (e.g., `interface vlan40`)
- Dot1Q encapsulation
- Interface descriptions (optional metadata)

## 4. Device Configurations

### 4.1 Routers

The parser handles traditional routing devices running static or OSPF routes.

**Detected Configuration Patterns:**
- Static routes (`ip route ...`)
- OSPF process IDs and areas
- Interface IPs and shutdown status
- VLAN associations

**Example:**
```
interface GigabitEthernet0/0
 ip address 10.0.0.1 255.255.255.252
 no shutdown
router ospf 1
 network 10.0.0.0 0.0.0.3 area 0
```

### 4.2 Switches (L3 or L2)

Multilayer switch (MLS) interfaces are detected with:
- SVIs (e.g., `interface vlan10`)
- Routing enabled (`ip routing`)
- VLAN encapsulation for trunk/access ports

**Example:**
```
vlan 40
 name SERVERS
interface vlan 40
 ip address 192.168.40.1 255.255.255.0
 no shutdown
```

### 4.3 Stub Networks

Interfaces with IPs on subnets not shared with other devices are labeled as stub networks:
- Common in WAN edge links or server LANs
- Represented as special nodes in the topology

## 5. Security Features (Optional Enhancements)

Although the primary focus is topology mapping, the system can be extended to identify:
- Access Control Lists (ACLs)
- Port security via interface config
- SSH settings (`transport input ssh`, `crypto key generate`)
- Spanning Tree settings on edge switches

Future versions can tag devices/interfaces with security metadata.

## 6. Verification Checklist

- Interfaces and IPs correctly parsed from `config.dump`
- Subnets grouped by presence across multiple routers
- Point-to-point and stub links identified
- OSPF areas mapped to relevant interfaces
- VLANs discovered using SVI or encapsulation
- Final topology generated as `.png` using matplotlib

## 7. Network Diagrams

**Figure 1: Logical Topology**

This is an automatically generated graph showing:
- All routers and switches as nodes
- Inter-device links based on subnet matching
- Stub networks attached to single routers
- VLAN interfaces and SVI roles

**Output File:** `generated_topology.png`

Generated using: NetworkX, matplotlib, and your config parser

## 8. Finalized Working Topology

This diagram represents the fully discovered, connected, and labeled network as built from real-world configuration files stored in the `Conf/` directory.
- Each link has directionality and labels (interface-to-interface)
- Each router shows active interfaces and IPs
- Stub links show isolated segments (e.g., server nets)

The topology is suitable for:
- Documentation
- Network troubleshooting
- Change management
- Further automation (e.g., Ansible integration)

## 9. Conclusion

The network topology tool successfully automates the traditionally manual task of reading Cisco device configurations and building a real-time network map. It offers a powerful base for larger infrastructure-as-code solutions, automated documentation, and topology-aware monitoring systems.

This project aligns with Cisco's automation goals by demonstrating a zero-touch discovery workflow from raw router configs to full topology visualization.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Harshitha-27-cell/cisco-vip-2025.git
   cd cisco-vip-2025
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

   (Note: Create a `requirements.txt` with packages like `networkx`, `matplotlib`, etc.)

## Usage

1. Place your Cisco router configuration files (e.g., `config.dump`) in the `Conf/` directory, organized by device (e.g., `Conf/R1/config.dump`).

2. Run the main script:
   ```
   python main.py
   ```

3. The tool will parse the configurations, build the topology, and generate `generated_topology.png`.

## Project Structure

- `config_parser.py`: Custom configuration parser for Cisco configs.
- `topology_builder.py`: Automated topology builder using graph-based discovery.
- `main.py`: Main entry point to run the tool.
- `test_parser.py`: Unit tests for the parser.
- `Conf/`: Directory containing configuration files.
  - `R1/config.dump`
  - `R2/config.dump`
  - `R3/config.dump`
- `generated_topology.png`: Output topology diagram.
- `.gitignore`: Ignores virtual environment and other unnecessary files.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.