import socket

def is_connected(host="8.8.8.8", port=53, timeout=3):
    """
    Checks if there is an active internet connection by pinging Google DNS.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False

# Backward compatibility alias
def check_internet_connection():
    return is_connected()
