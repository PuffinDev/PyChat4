import socket
import json
import struct

def send(channel, msg):
    msg = json.dumps(msg).encode()
    try:
        channel.send(struct.pack("i", len(msg)) + msg)
    except (ConnectionResetError, BrokenPipeError):
        pass


def receive(channel):
    try:
        size = struct.unpack("i", channel.recv(struct.calcsize("i")))[0]
        if size > 10000:
            return False
        data = ""
        while len(data) < size:
            msg = channel.recv(size - len(data))
            if not msg:
                return None
            try:
                data += msg.decode()
            except Exception as e:
                return None
        return json.loads(data.strip())
    except (OSError, json.JSONDecodeError, struct.error) as e:
        return False
