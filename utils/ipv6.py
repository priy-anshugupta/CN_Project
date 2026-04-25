import ipaddress

def calculate_ipv6(ip_str):
    try:
        if '/' not in ip_str:
            return {"Valid": False, "Error": "Please provide a prefix length (e.g., 2001:db8::/32)"}
        
        network = ipaddress.IPv6Network(ip_str, strict=False)
        ip = ipaddress.IPv6Address(ip_str.split('/')[0])
        
        # Safe calc for subnets based on /64 standard LAN boundary
        prefix_diff = 64 - network.prefixlen
        if prefix_diff > 0:
            lan_subnets = 2 ** prefix_diff
            lan_subnets_str = f"{lan_subnets:,}"
        elif prefix_diff == 0:
             lan_subnets_str = "1"
        else:
             lan_subnets_str = "N/A (Prefix is > 64)"
        
        # Using string representation for massive numbers
        total_ips = str(network.num_addresses)
        if len(total_ips) > 10:
             total_ips = f"{network.num_addresses:.2e}"
             
        return {
            "Valid": True,
            "IP Address (Expanded)": ip.exploded,
            "IP Address (Compressed)": ip.compressed,
            "Network Address": f"{network.network_address}/{network.prefixlen}",
            "Prefix Length": str(network.prefixlen),
            "Total Subnets (/64)": lan_subnets_str,
            "Total Addresses": total_ips,
            "Is Private": "Yes" if network.is_private else "No",
            "Site Local": "Yes" if network.is_site_local else "No",
            "Loopback": "Yes" if network.is_loopback else "No",
            "Link Local": "Yes" if network.is_link_local else "No"
        }
    except ValueError as e:
         return {"Valid": False, "Error": str(e)}
