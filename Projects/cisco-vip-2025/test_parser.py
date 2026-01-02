def test_interface_parsing():
    # Test R1 config
    with open('Conf/R1/config.dump', 'r') as f:
        r1_config = f.read()
    
    print("=== R1 CONFIG CONTENT ===")
    print(repr(r1_config[:500]))  # Show first 500 characters
    print("...")
    
    # Look for interface patterns
    lines = r1_config.split('\n')
    interface_lines = [line for line in lines if 'interface' in line.lower()]
    print("Interface lines found in R1:", interface_lines)
    
    # Test R2 config
    with open('Conf/R2/config.dump', 'r') as f:
        r2_config = f.read()
    
    print("\n=== R2 CONFIG CONTENT ===")
    interface_lines = [line for line in r2_config.split('\n') if 'interface' in line.lower()]
    print("Interface lines found in R2:", interface_lines)
    
    # Test R3 config
    with open('Conf/R3/config.dump', 'r') as f:
        r3_config = f.read()
    
    print("\n=== R3 CONFIG CONTENT ===")
    interface_lines = [line for line in r3_config.split('\n') if 'interface' in line.lower()]
    print("Interface lines found in R3:", interface_lines)

if __name__ == "__main__":
    test_interface_parsing()