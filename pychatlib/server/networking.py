import json
import socket
import select

def receive(conn):
    msg = b""
    
    conn.setblocking(0)

    while True:
        try:
            ready = select.select([conn], [], [], 0.1)
            if ready[0]:
                packet = conn.recv(64)
                #print(f"Received packet: {packet.decode()}")
            else:
                break
        except socket.error:
            break

        if not packet:
            return False
    
        msg += packet

    try:
        json_msg = json.loads(msg.decode())
    except:
        return None

    if not json_msg:
        return None

    #print(f"|{msg.decode()}|")
    return json_msg

def send(conn, msg):
    msg = json.dumps(msg).encode()
    conn.send(msg)

