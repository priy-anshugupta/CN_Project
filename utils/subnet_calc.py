import ipaddress

def calculate_subnet(ip_str):
    try:
        if '/' not in ip_str and ' ' not in ip_str:
            return {"Valid": False, "Error": "Please provide a CIDR prefix (e.g., 192.168.1.0/24) or Subnet Mask (e.g., 192.168.1.0 255.255.255.0)"}
            
        if ' ' in ip_str:
             ip_part, mask_part = ip_str.split(' ')
             network = ipaddress.IPv4Network(f"{ip_part}/{mask_part}", strict=False)
             ip = ipaddress.IPv4Address(ip_part)
        else:
            network = ipaddress.IPv4Network(ip_str, strict=False)
            ip = ipaddress.IPv4Address(ip_str.split('/')[0])
        
        # Calculate wild card mask
        netmask = int(network.netmask)
        wildcard_mask = str(ipaddress.IPv4Address((~netmask) & 0xFFFFFFFF))
        
        # Determine class (historical)
        first_octet = int(str(ip).split('.')[0])
        if 1 <= first_octet <= 126: ip_class = 'A'
        elif 128 <= first_octet <= 191: ip_class = 'B'
        elif 192 <= first_octet <= 223: ip_class = 'C'
        elif 224 <= first_octet <= 239: ip_class = 'D (Multicast)'
        elif 240 <= first_octet <= 255: ip_class = 'E (Experimental)'
        else: ip_class = 'Unknown'
        
        # Get binary representation
        ip_binary = '.'.join([f"{int(x):08b}" for x in str(ip).split('.')])
        mask_binary = '.'.join([f"{int(x):08b}" for x in str(network.netmask).split('.')])
        
        usable_hosts = network.num_addresses - 2 if network.num_addresses > 2 else 0
        if network.prefixlen in (31, 32):
            usable_hosts = network.num_addresses
            
        hosts_list = list(network.hosts())
        first_host = str(hosts_list[0]) if hosts_list else "N/A"
        last_host = str(hosts_list[-1]) if hosts_list else "N/A"
        
        # Binary representations of Network Address and Broadcast Address
        network_binary = '.'.join([f"{int(x):08b}" for x in str(network.network_address).split('.')])
        broadcast_binary = '.'.join([f"{int(x):08b}" for x in str(network.broadcast_address).split('.')]) if network.prefixlen < 31 else "N/A"

        # Build detailed calculation steps with working
        steps = [
            f"**Step 1: Identify IP and Mask**\n"
            f"- Given Input: `{ip_str}`\n"
            f"- IP Address: `{str(ip)}`\n"
            f"- Prefix Length (CIDR): `/{network.prefixlen}`\n",
            
            f"**Step 2: Convert to Binary**\n"
            f"- IP Address (Binary): `{ip_binary}`\n"
            f"- Subnet Mask (Binary): `{mask_binary}` (={network.prefixlen} ones followed by {32 - network.prefixlen} zeros)\n"
            f"- Subnet Mask (Decimal): `{str(network.netmask)}`\n",
            
            f"**Step 3: Calculate Hosts**\n"
            f"- Host Bits ($h$) = $32 - \\text{{prefix}}$ = $32 - {network.prefixlen}$ = `{32 - network.prefixlen}`\n"
            f"- Total Hosts = $2^h$ = $2^{{{32 - network.prefixlen}}}$ = `{network.num_addresses}`\n"
            f"- Usable Hosts = Total Hosts - 2 (Network & Broadcast) = `{network.num_addresses} - 2` = `{usable_hosts}`\n",
            
            f"**Step 4: Calculate Network Address**\n"
            f"Perform Bitwise AND between IP and Subnet Mask:\n"
            f"  `{ip_binary}` (IP)\n"
            f"& `{mask_binary}` (Mask)\n"
            f"--------------------------------------------------\n"
            f"  `{network_binary}` -> Decimal: `{network.network_address}`\n",
            
            f"**Step 5: Calculate Broadcast Address**\n"
            f"Set all host bits (last {32 - network.prefixlen} bits) of Network Address to 1:\n"
            f"  `{network_binary}` (Network)\n"
            f"| `{'0'*network.prefixlen + '1'*(32 - network.prefixlen)}` (inverted mask)\n"
            f"--------------------------------------------------\n"
            f"  `{broadcast_binary}` -> Decimal: `{str(network.broadcast_address) if network.prefixlen < 31 else 'N/A'}`\n",
            
            f"**Step 6: Determine Key Addresses**\n"
            f"Based on the Network and Broadcast addresses, we can find the usable range:\n"
            f"- **Network Address:** `{network.network_address}`\n"
            f"- **First Usable Address:** `{first_host}` (Network Address + 1)\n"
            f"- **Last Usable Address:** `{last_host}` (Broadcast Address - 1)\n"
            f"- **Broadcast Address:** `{str(network.broadcast_address) if network.prefixlen < 31 else 'N/A'}`\n"
        ]
        
        return {
            "Valid": True,
            "Network Address": f"{network.network_address}/{network.prefixlen}",
            "Broadcast Address": str(network.broadcast_address) if network.prefixlen < 31 else "N/A",
            "Subnet Mask": str(network.netmask),
            "Subnet Mask (Hex)": hex(int(network.netmask)),
            "Subnet Mask (Binary)": mask_binary,
            "Wildcard Mask": wildcard_mask,
            "Total Hosts": network.num_addresses,
            "Usable Hosts": usable_hosts,
            "First Usable Host": first_host,
            "Last Usable Host": last_host,
            "IP Class": ip_class,
            "IP Address (Binary)": ip_binary,
            "Is Private": network.is_private,
            "Steps": steps,
        }
        
    except ValueError as e:
        return {"Valid": False, "Error": str(e)}

def generate_subnets(ip_str):
    try:
        network = ipaddress.IPv4Network(ip_str, strict=False)
        subnets = list(network.subnets())
        # To avoid massive output, limit if very large
        if len(subnets) > 4096:
            return {"Valid": False, "Error": "Too many subnets to generate (max 4096). Please try a larger subnet mask."}
        
        res = []
        for subnet in subnets:
            hosts = list(subnet.hosts())
            res.append({
                "Network": str(subnet.network_address),
                "CIDR": f"/{subnet.prefixlen}",
                "Mask": str(subnet.netmask),
                "Broadcast": str(subnet.broadcast_address) if subnet.prefixlen < 31 else "N/A",
                "First Host": str(hosts[0]) if hosts else "N/A",
                "Last Host": str(hosts[-1]) if hosts else "N/A",
                "Usable Hosts": subnet.num_addresses - 2 if subnet.num_addresses > 2 else subnet.num_addresses
            })
        return {"Valid": True, "Subnets": res}
    except ValueError as e:
        return {"Valid": False, "Error": str(e)}
