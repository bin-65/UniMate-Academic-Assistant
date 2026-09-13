import socket

def check_internet_connection():
    try:
        # Check if internet/Google DNS is reachable
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False
