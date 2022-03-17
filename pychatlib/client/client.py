import socket
import json
from threading import Thread
from random import choice
from hashlib import sha256
from tkinter import *

from .networking import receive, send_message, send_command
from .config import THEMES, DEFAULT_SERVER, DEFAULT_USERNAME

class Client:
    def __init__(self):
        self.JOIN_MESSAGES = ["just joined!", "has joined", "has entered the chat", "arrived!", "slid in!", "showed up!", "joined the party!"]
        self.LEAVE_MESSAGES = ["left the chat", "has left", "just left", "has exited", "flew away!"]
        self.DEFAULT_SERVER = DEFAULT_SERVER
        self.theme = THEMES["sweden"]
        self.system_message_indexes = []
        self.username = DEFAULT_USERNAME
        self.login_status = ""

        self.server_address = ["0.0.0.0", 8888]

        self.logon_gui()
        self.init_main_gui()
        self.init_socket()
        self.gui_mainloop()

    def logon_gui(self):
        self.logon_win = Tk()
        self.logon_win.title("PyChat4")
        self.logon_win.geometry("190x260")
        self.logon_win.resizable(False, False)
        self.logon_win.tk_setPalette(background=self.theme["bg"], foreground=self.theme["fg"],
               activeBackground=self.theme["bg2"], activeForeground=self.theme["fg"])
        self.logon_win.protocol("WM_DELETE_WINDOW", exit)

        main_title = Label(text="PyChat4", font=("", 16))
        main_title.pack()
        Label().pack()
        title = Label(text="Server", font=("", 11))
        title.pack()
        server_entry = Entry(background=self.theme["bg2"], justify="center")
        server_entry.insert(END, self.DEFAULT_SERVER)
        server_entry.pack()
        title2 = Label(text="Username", font=("", 11))
        title2.pack()
        username_entry = Entry(background=self.theme["bg2"], justify="center")
        username_entry.pack()
        title3 = Label(text="Password", font=("", 11))
        title3.pack()
        password_entry = Entry(background=self.theme["bg2"], justify="center", show="*")
        password_entry.pack()
        Label().pack()
        connect_button = Button(text="Join", command=lambda: self.set_server(server_entry.get(), username_entry.get(), password_entry.get()), background=self.theme["bg2"])
        connect_button.pack()

        self.logon_win.mainloop()

    def set_server(self, server_address, username, password):
        if server_address:
            self.server_address[0] = server_address.strip()
        if username:
            self.username = username.strip()
        self.password = sha256(password.strip().encode()).hexdigest()
        self.logon_win.destroy()

    def init_main_gui(self):
        self.root = Tk()
        self.root.title("PyChat4")
        self.root.geometry("600x350")
        self.root.resizable(False, False)

        self.root.tk_setPalette(background=self.theme["bg"], foreground=self.theme["fg"],
               activeBackground=self.theme["bg2"], activeForeground=self.theme["fg"])

        self.messages = Listbox(width=60, height=10, font=("", 11), bg=self.theme["bg2"], selectbackground=self.theme["bg2"], selectforeground=self.theme["fg"])
        self.messages.grid(pady=(25,15))
        self.insert_system_message("Welcome to PyChat!")

        self.userlist = Listbox(width=14, height=10, font=("", 11), bg=self.theme["bg2"])
        self.userlist.grid(row=0, column=1, pady=(25,15))

        self.messagebox_var = StringVar()
        self.messagebox = Entry(textvariable=self.messagebox_var, width=25, font=("", 11))
        self.messagebox.bind("<Return>", self.send)
        self.messagebox.focus_set()
        self.messagebox.grid()

        self.send_message_button = Button(text="Send", font=("", 12), command=self.send, bg=self.theme["bg2"])
        self.send_message_button.grid(pady=(5, 5))

    def set_gui_theme(self):
        self.root.tk_setPalette(background=self.theme["bg"], foreground=self.theme["fg"],
               activeBackground=self.theme["bg2"], activeForeground=self.theme["fg"])

        self.messages.config(bg=self.theme["bg2"], selectbackground=self.theme["bg2"], selectforeground=self.theme["fg"])
        self.send_message_button.config(bg=self.theme["bg2"])
        self.userlist.config(bg=self.theme["bg2"])

        for i in self.system_message_indexes:
            self.messages.itemconfig(i, {"fg": self.theme["fg_highlight"], "selectforeground": self.theme["fg_highlight"]})

    def gui_mainloop(self):
        self.root.mainloop()

    def init_socket(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(tuple(self.server_address))

        thread = Thread(target=self.receive_loop, daemon=True)
        thread.start()

        send_command(self.s, {"command": "login", "username": self.username, "password": self.password, "manual_call": False})

    def insert_message(self, msg):
        self.messages.insert(END, f"{msg}")
        self.messages.yview(END)

    def insert_system_message(self, msg):
        self.messages.insert(END, msg)
        msg_index = self.messages.size()-1
        self.system_message_indexes.append(msg_index)
        self.messages.itemconfig(msg_index, {"fg": self.theme["fg_highlight"], "selectforeground": self.theme["fg_highlight"]})
        self.messages.yview(END)

    def insert_command_response(self, command, messages):
        start_index = self.messages.size()
        self.messages.insert(END, f"You used /{command}:")
        for msg in messages:
            self.messages.insert(END, f"|   {msg}")

        for i in range(start_index, self.messages.size()):
            self.system_message_indexes.append(i)
            self.messages.itemconfig(i, {"fg": self.theme["fg_highlight"], "selectforeground": self.theme["fg_highlight"]})

        self.messages.yview(END)

    def exit(self):
        msg = {
            "command": "exit"
        }

        send_command(self.s, msg)

        exit()

    def set_username(self, username):
        msg = {
            "command": "set_username",
            "username": username
        }

        send_command(self.s, msg)

        self.insert_command_response("username", [f"Set username to {username}"])

    def request_users(self):
        msg = {
            "command": "users",
            "manual_call": True
        }

        send_command(self.s, msg)

    def direct_message(self, args):
        if not " " in args:
            return False

        user, message = args.split(" ", 1)

        msg = {
            "command": "dm",
            "recipient": user,
            "message": message
        }

        send_command(self.s, msg)
        return True

    def login(self, args):
        msg = {
            "command": "login",
            "username": args[0],
            "password": args[1],
            "manual_call": True
        }

        send_command(self.s, msg)

    def send(self, *a):
        msg = self.messagebox_var.get()
        if len(msg) < 1:
            return
        if msg[0] != "/":
            send_message(self.s, msg)
        else:
            if " " in msg:
                command, args = msg[1:].split(" ", 1)
            else:
                command = msg[1:]

            if command == "exit":
                self.exit()
            elif command == "username":
                self.set_username(args)
            elif command == "users":
                self.request_users()
            elif command == "theme":
                if args in THEMES:
                    self.theme = THEMES[args]
                    self.set_gui_theme()
                    self.insert_command_response("theme", [f"Set theme to {args}"])
                else:
                    self.insert_command_response("theme", [f"That is not a valid theme. Use /themes to see them"])
            elif command == "themes":
                msg = ["Themes: "]
                for i, theme in enumerate(THEMES):
                    if i == 0:
                        msg[0] += f"{theme}"
                    else:
                        msg[0] += f", {theme}"

                self.insert_command_response("themes", msg)
            elif command == "dm":
                if self.direct_message(args):
                    self.insert_command_response(f"dm {args.split(' ', 1)[0]}", [f"{args.split(' ', 1)[1]}"])
            elif command == "login":
                if not args:
                    self.insert_command_response("login", ["Invalid arguments. Please use /login <username> <password>"])
                args = args.split(" ")
                if len(args) < 2:
                    self.insert_command_response("login", ["Invalid arguments. Please use /login <username> <password>"])

                self.login(args)
            else:
                self.insert_command_response(command, ["That is not a valid command."])

        self.messagebox_var.set("")


    def receive_loop(self):
        while True:
            messages = receive(self.s)
            if not messages:
                continue

            for msg in messages:
                if msg == None:
                    continue

                if msg["command"] == "message":
                    self.insert_message(f"{msg['author']['username']}: {msg['message']}")

                elif msg["command"] == "server_message":
                    self.insert_system_message(f"[SERVER] {msg['message']}")

                elif msg["command"] == "dm":
                    self.insert_message(f"[DM] {msg['author']['username']}: {msg['message']}")

                elif msg["command"] == "user_join":
                    self.insert_system_message(f"> {msg['user']} {choice(self.JOIN_MESSAGES)}")

                elif msg["command"] == "user_leave":
                    self.insert_system_message(f"< {msg['user']} {choice(self.LEAVE_MESSAGES)}")

                elif msg["command"] == "users":
                    if msg["manual_call"]:
                        self.insert_command_response("users", msg["users"])

                    self.userlist.delete(0,END)
                    for user in msg["users"]:
                        self.userlist.insert(END, user)

                elif msg["command"] == "result":
                    if msg["result"] == "invalid_password":
                        if not msg["manual_call"]:
                            self.insert_system_message("Invalid password. Please try again with /login <user> <pass>")
                        else:
                            self.insert_command_response("login", ["Invalid password"])
                        self.login_status = msg["result"]
                    if msg["result"] == "created_account":
                        if not msg["manual_call"]:
                            self.insert_system_message("New account created!")
                        else:
                            self.insert_command_response("login", ["New account created!"])
                        self.login_status = msg["result"]
                    if msg["result"] == "login_success":
                        self.login_status = msg["result"]
                        if msg["manual_call"]:
                            self.insert_command_response("login", ["Logged in sucessfully"])
