import json
import socket
import select
import re

def receive(conn):
    msg = b""
    conn.setblocking(0)

    while True:
        try:
            ready = select.select([conn], [], [], 0.1)
            if ready[0]:
                packet = conn.recv(64)
            else:
                break
        except socket.error:
            break
        if not packet:
            return False

        msg += packet

        try:
            json.loads(msg.decode())
            break
        except:
            pass

    msg = msg.decode()
    messages = []

    messages = re.split(r"(?<=})(?={)", msg)

    for message in messages:
        if message == "":
            messages.remove(message)

    json_messages = []

    for msg in messages:
        try:
            json_messages.append(json.loads(msg))
        except:
            return None

    return json_messages

def send_message(s, text):
    s.send(json.dumps({
        "command": "message",
        "message": f"{text}"
    }).encode())

def send_command(s, msg):
    s.send(json.dumps(msg).encode())
