import socket
import logging
import time
import json
from .networking import send, receive
from .messages import *
from threading import Thread

from .models import Client, User

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
        self.ADMIN_USERID = 0

        with open("banned_ips.json") as f:
            self.banned_ips = json.load(f)

        with open("users.json") as f:
            json_users = json.load(f)

        for user in json_users:
            self.users.append(User().from_json(user))

    def update_users(self):
        self.broadcast_message(online_users_message(self.clients, manual_call=False))

    def username_to_user(self, username):
        for user in self.users:
            if user.username == username:
                return user
    
    def username_to_client(self, username):
        for client in self.clients:
            if client.user.username == username:
                return client

    def user_exists(self, username):
        for user in self.users:
            if user.username == username:
                return True
    
        return False

    def save_users(self):
        users_json = []

        for user in self.users:
            users_json.append(user.json())

        with open("users.json", "w") as f:
            json.dump(users_json, f)

    def save_banned_ips(self):
        with open("banned_ips.json", "w") as f:
            json.dump(self.banned_ips, f)


    def broadcast_message(self, msg):
        for client in self.clients:
            send(client.connection, msg)

    def handle_client(self, client):
        while not client.user:
            msg = receive(client.connection)

            if msg == False:
                self.clients.remove(client)
                return
            if msg == None:
                continue

            self.handle_login(msg, client)

        if client.address[0] in self.banned_ips:
            send(client.connection, banned_message())
            self.users.remove(client.user)
            self.update_users()
            return False

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

            if client not in self.clients:
                # client has been banned
                return False

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
                        send(client.connection, result_message("login", "success", manual_call=msg["manual_call"]))
                        return True
                    else:
                        send(client.connection, result_message("login", "invalid_password", manual_call=msg["manual_call"]))
                        return False

            # create account
            self.users.append(User().from_json({
                "username": msg["username"],
                "password": msg["password"],
                "roles": [],
                "id": len(self.users)
            }))
            self.save_users()

            client.user = self.users[-1]

            send(client.connection, result_message("login", "created_account", manual_call=msg["manual_call"]))

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

        elif msg["command"] == "online_users":
            send(client.connection, online_users_message(self.clients, manual_call=msg["manual_call"]))

        elif msg["command"] == "users":
            send(client.connection, users_message(self.clients, self.users))

        elif msg["command"] == "dm":
            matching_users = []
            for c in self.clients:
                if c.user.username == msg["recipient"]:
                    matching_users.append(c)

            if len(matching_users) != 1:
                return False
            recipient = matching_users[0]

            send(recipient.connection, direct_message(client.user.info_json(), msg["message"]))

        elif msg["command"] == "addrole":
            if not self.username_to_user(msg["username"]):
                send(client.connection, result_message("addrole", "invalid_user"))
                return False

            if "admin" not in client.user.roles and self.ADMIN_USERID != client.user.id:
                send(client.connection, result_message("addrole", "insufficient_perms"))
                return False

            for user in self.users:
                if user.username == msg["username"]:
                    user.roles.append(msg["role"])
                    self.update_users()
                    self.save_users()
                    send(client.connection, result_message("addrole", "success"))

        elif msg["command"] == "delete_account":
            if "admin" not in client.user.roles:
                send(client.connection, result_message("delete_account", "insufficient_perms"))
                return False

            if not self.user_exists(msg["username"]):
                send(client.connection, result_message("delete_account", "invalid_user"))
                return False
            
            
            if self.delete_account(msg["username"]):
                send(client.connection, result_message("delete_account", "success"))
        
        elif msg["command"] == "ban":
            if "admin" not in client.user.roles:
                send(client.connection, result_message("ban", "insufficient_perms"))
                return False

            arg_client = self.username_to_client(msg["username"])
            if not arg_client:
                if not self.user_exists(msg["username"]):
                    send(client.connection, result_message("ban", "invalid_user"))
                    return False
                else:
                    send(client.connection, result_message("ban", "user_offline"))
                    return False
            
            
            self.delete_account(arg_client.user.username)
            self.banned_ips.append(arg_client.address[0])
            self.save_banned_ips()

            for c in self.clients:
                if c.user.username == msg["username"]:
                    send(c.connection, banned_message())
                    self.clients.remove(c)
                    self.update_users()
                    self.save_users()
                    break

            send(client.connection, result_message("ban", "success"))

    def delete_account(self, username):
        for user in self.users:
            if user.username == username:
                self.users.remove(user)
                break
        
        self.save_users()
        self.update_users()
        
        return True

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind(("0.0.0.0", 8888))

        sock.listen()

        current_id = 0

        while True:
            try:
                conn, addr = sock.accept()
                logging.info(f"New connection to {addr}")

                client = Client(conn, addr, current_id)

                thread = Thread(target=self.handle_client, args=(client,), daemon=True)
                thread.start()

                self.clients.append(client)
                current_id += 1

            except KeyboardInterrupt:
                logging.info("Server shutdown")
                self.broadcast_message(server_message("Server shutdown"))
                sock.close()
                break
