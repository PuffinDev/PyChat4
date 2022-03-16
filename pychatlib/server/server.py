import socket
import logging
import time
import json
from .networking import send, receive
from .messages import *
from threading import Thread

from .client import Client, User

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
        self.users = []

        with open("users.json") as f:
            json_users = json.load(f)

        for user in json_users:
            self.users.append(User().from_json(user))

    def broadcast_message(self, msg):
        for client in self.clients:
            send(client.connection, msg)
            logging.debug(f"sent {msg['command']} to {client.user.info_json()}")

    def update_users(self):
        self.broadcast_message(users_message(self.clients, manual_call=False))

    def save_users(self):
        users_json = []
        
        for user in self.users:
            users_json.append(user.json())

        with open("users.json", "w") as f:
            json.dump(users_json, f)

    def handle_client(self, client):

        while not client.user:
            msg = receive(client.connection)
            if msg == False:
                self.clients.remove(client)
                return
            if msg == None:
                continue

            self.handle_login(msg, client)

        self.broadcast_message(join_message(client.user.username))

        self.update_users()

        while True:
            try:
                msg = receive(client.connection)
            except BrokenPipeError:
                break
            if msg == False:
                break
            elif msg == None:
                continue
            elif not msg:
                continue

            self.handle_message(msg, client)

        logging.info(f"Client left: {client.user.username}")
        self.broadcast_message(leave_message(client.user.username))
        self.clients.remove(client)
        self.update_users()
        return

    def handle_login(self, msg, client):
        if msg["command"] == "login":
            for user in self.users:
                if user.username == msg["username"]:
                    if user.password == msg["password"]:
                        client.user = user
                        send(client.connection, result_message("login_success", manual_call=msg["manual_call"]))
                        return True
                    else:
                        send(client.connection, result_message("invalid_password", manual_call=msg["manual_call"]))
                        return False

            # create account
            self.users.append(User().from_json({
                "username": msg["username"],
                "password": msg["password"],
                "id": len(self.users)
            }))
            self.save_users()

            client.user = self.users[-1]

            send(client.connection, result_message("created_account", manual_call=msg["manual_call"]))

        return False

    def handle_message(self, msg, client):
        if msg["command"] == "message":
            msg["author"] = client.user.info_json()
            self.broadcast_message(msg)

        elif msg["command"] == "set_username":
            for user in self.users:
                if user.username == msg["username"]:
                    return
            
            client.user.username = msg["username"]
            self.update_users()
            self.save_users()

        elif msg["command"] == "users":
            send(client.connection, users_message(self.clients, manual_call=msg["manual_call"]))

        elif msg["command"] == "dm":
            matching_users = []
            for c in self.clients:
                if c.user.username == msg["recipient"]:
                    matching_users.append(c)

            if len(matching_users) != 1:
                return False
            recipient = matching_users[0]

            send(recipient.connection, direct_message(client.user.info_json(), msg["message"]))

        else:
            logging.debug("Invalid message: \n" + str(msg))

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.bind(("0.0.0.0", 8888))

        sock.listen()

        while True:
            try:
                current_id = 0

                conn, addr = sock.accept()
                logging.info(f"New connection to {addr}")

                client = Client(conn, addr, current_id)

                thread = Thread(target=self.handle_client, args=(client,), daemon=True)
                thread.start()

                self.clients.append(client)
                current_id += 1

            except KeyboardInterrupt:
                self.broadcast_message({"command": "server_message", "message": "server shutdown"})
                sock.close()
                break
