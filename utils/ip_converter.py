import ipaddress

def ip_to_binary(ip_str):
    try:
        ip = ipaddress.IPv4Address(ip_str)
        return '.'.join([f"{int(x):08b}" for x in str(ip).split('.')])
    except:
        return "Invalid IP"

def binary_to_ip(bin_str):
    try:
        parts = bin_str.split('.')
        return '.'.join([str(int(p, 2)) for p in parts])
    except:
        return "Invalid Binary IP Form. Expected format: 11000000.10101000.00000001.00000001"

def ip_to_hex(ip_str):
    try:
        ip = ipaddress.IPv4Address(ip_str)
        return '.'.join([hex(int(x))[2:].zfill(2).upper() for x in str(ip).split('.')])
    except:
        return "Invalid IP"

def hex_to_ip(hex_str):
    try:
        parts = hex_str.split('.')
        return '.'.join([str(int(p, 16)) for p in parts])
    except:
        return "Invalid Hex IP Form. Expected format: C0.A8.01.01"

def cidr_to_mask(cidr):
    try:
        c = int(cidr.replace('/', ''))
        return str(ipaddress.IPv4Network(f"0.0.0.0/{c}").netmask)
    except:
        return "Invalid CIDR"

def mask_to_cidr(mask):
    try:
        return f"/{str(ipaddress.IPv4Network(f'0.0.0.0/{mask}').prefixlen)}"
    except:
        return "Invalid Subnet Mask"
