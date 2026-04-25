import ipaddress
import math

def calculate_vlsm(base_ip, hosts_list):
    try:
        network = ipaddress.IPv4Network(base_ip, strict=False)
        
        # Sort host requirements descending
        hosts_list = sorted([h for h in hosts_list if h > 0], reverse=True)
        
        subnets = []
        current_ip = int(network.network_address)
        
        for idx, hosts in enumerate(hosts_list):
            needed_size = hosts + 2
            power = math.ceil(math.log2(needed_size))
            actual_size = 2 ** power
            prefixlen = 32 - power
            
            if current_ip + actual_size > int(network.broadcast_address) + 1:
                return {"Valid": False, "Error": "Base network too small to accommodate all requesting subnets. Failed at subnet requesting " + str(hosts) + " hosts."}
            
            subnet = ipaddress.IPv4Network((current_ip, prefixlen))
            usable_hosts = list(subnet.hosts())
            
            subnets.append({
                "Name": f"Subnet {idx+1}",
                "Requested Hosts": hosts,
                "Allocated Size": actual_size,
                "Usable Hosts": actual_size - 2 if actual_size > 2 else actual_size,
                "Network Address": str(subnet.network_address),
                "CIDR": f"/{subnet.prefixlen}",
                "Subnet Mask": str(subnet.netmask),
                "First Host": str(usable_hosts[0]) if usable_hosts else "N/A",
                "Last Host": str(usable_hosts[-1]) if usable_hosts else "N/A",
                "Broadcast Address": str(subnet.broadcast_address)
            })
            
            current_ip += actual_size
            
        # Unallocated space calc
        unallocated_size = (int(network.broadcast_address) + 1) - current_ip
        
        return {"Valid": True, "Subnets": subnets, "Unallocated": unallocated_size}
        
    except ValueError as e:
        return {"Valid": False, "Error": format_error(str(e))}

def format_error(e):
    return f"Invalid Network: {e}. Example format: 192.168.1.0/24"

def summarize_routes(network_list):
    try:
        networks = []
        for net in network_list:
             if net.strip():
                 networks.append(ipaddress.IPv4Network(net.strip(), strict=False))
        
        summarized = list(ipaddress.collapse_addresses(networks))
        return {"Valid": True, "Summarized": [f"{net.network_address}/{net.prefixlen}" for net in summarized]}
    except ValueError as e:
        return {"Valid": False, "Error": f"Invalid network in list: {str(e)}"}
