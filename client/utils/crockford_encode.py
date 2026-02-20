import socket
import struct
from base32_crockford import encode,decode #crockford is a variant of base32 that removes often mistyped letters from the dictionary to avoid typos during manual writing

def get_local_ip()->str:
    """
    Returns the (primary) local ipv4 addres
    
    :return: the address
    :rtype: str
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80)) #just to trigger route resolution
        return s.getsockname()[0]

def address_encode(port:int)->str:
    """
    Generates a pairing code using crockford encocode
    :param port: The port to be accessed
    :type port: int
    :return: A pairing code including the address, port, version byte and checksum
    :rtype: str
    """
    ip_str = get_local_ip()
    ip_bytes = socket.inet_aton(ip_str)
    port_bytes = struct.pack("!H", port)
    version_byte = struct.pack("!B", 1)

    data = ip_bytes + port_bytes + version_byte  # 7 bytes

    # Convert bytes to integer
    value = int.from_bytes(data, byteorder="big")

    # Encode with checksum
    code = encode(value, checksum=False)
    
    return "-".join([code[i:i+4] for i in range(0, len(code), 4)]) #groups separated by "-" to be more human readable


def address_decode(code: str):
    cleaned = code.replace("-", "")
    value = decode(cleaned, checksum=True)  # integer
    data_bytes = value.to_bytes(7, byteorder="big")  # convert back to 7 bytes
    ip_bytes = data_bytes[0:4]
    port_bytes = data_bytes[4:6]
    version = data_bytes[6]

    ip_str = socket.inet_ntoa(ip_bytes)
    port = struct.unpack("!H", port_bytes)[0]
    return ip_str, port, version