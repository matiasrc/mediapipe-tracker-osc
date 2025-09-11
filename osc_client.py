from pythonosc.udp_client import SimpleUDPClient
import math

def sanitize_payload(payload):
    clean = []
    for v in payload:
        if isinstance(v, int):   # 👈 dejamos los int como int
            clean.append(v)
        elif isinstance(v, float):
            if v != v:  # NaN check
                clean.append(0.0)
            elif v == float("inf") or v == float("-inf"):
                clean.append(0.0)
            else:
                clean.append(v)
        else:
            try:
                clean.append(float(v))
            except:
                clean.append(0.0)
    return clean

class OSCClient:
    def __init__(self, ip: str = "127.0.0.1", port: int = 3333):
        self.client = None
        self.set_target(ip, port)

    def set_target(self, ip: str, port: int):
        self.client = SimpleUDPClient(ip, int(port))

    def send(self, address: str, data):
        if not self.client:
            return
        data = sanitize_payload(data)
        self.client.send_message(address, data)