import socket
import logging
from .networking import send, receive
from .messages import *
from threading import Thread

from .client import Client

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='server.log',
                    filemode='w')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)


class Server:
    def __init__(self):
        self.clients = []

    def broadcast_message(self, msg):
        for client in self.clients:
            send(client.connection, msg)

    def handle_client(self, client):
        msg = receive(client.connection)
        self.handle_message(msg, client)

        self.broadcast_message(join_message(client.username))

        while True:
            try:
                msg = receive(client.connection)
            except BrokenPipeError:
                break
            if msg == False:
                break
            elif msg == None:
                continue

            self.handle_message(msg, client)
        
        logging.info(f"Client left: {client.username}")
        self.clients.remove(client)
        self.broadcast_message(leave_message(client.username))
        return

    def handle_message(self, msg, client):
        if msg["command"] == "message":
            msg["author"] = client.json()
            self.broadcast_message(msg)

        elif msg["command"] == "set_username":
            client.username = msg["username"]
        
        elif msg["command"] == "users":
            self.broadcast_message(users_message(self.clients))
        
        else:
            print(msg)

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.bind(("0.0.0.0", 5555))

        sock.listen()

        while True:
            current_id = 0

            conn, addr = sock.accept()
            logging.info(f"New connection to {addr}")

            client = Client(conn, addr, current_id)

            thread = Thread(target=self.handle_client, args=(client,))
            thread.start()

            self.clients.append(client)
            current_id += 1
