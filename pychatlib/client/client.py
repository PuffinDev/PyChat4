import socket
import json
from threading import Thread
from random import choice
from hashlib import sha256
from tkinter import *
from playsound import playsound

from .networking import receive, send_message, send_command
from .config import THEMES, DEFAULT_SERVER, DEFAULT_USERNAME, DEFAULT_THEME

class Client:
    def __init__(self):
        self.JOIN_MESSAGES = ["just joined!", "has joined", "has entered the chat", "arrived!", "slid in!", "showed up!", "joined the party!"]
        self.LEAVE_MESSAGES = ["left the chat", "has left", "just left", "has exited", "flew away!"]
        self.DEFAULT_SERVER = DEFAULT_SERVER
        self.theme = THEMES[DEFAULT_THEME]
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
        self.logon_win.geometry("190x290")
        self.logon_win.resizable(False, False)
        self.logon_win.tk_setPalette(background=self.theme["bg"], foreground=self.theme["fg"],
               activeBackground=self.theme["bg2"], activeForeground=self.theme["fg"])
        self.logon_win.protocol("WM_DELETE_WINDOW", exit)

        main_title = Label(text="PyChat4", font=("", 16))
        main_title.pack()
        Label().pack()
        title = Label(text="Server", font=("", 12))
        title.pack()
        self.server_entry = Entry(background=self.theme["bg2"], justify="center", font=("", 12))
        self.server_entry.insert(END, self.DEFAULT_SERVER)
        self.server_entry.pack()
        self.server_entry.bind("<Return>", self.set_filled_in)
        title2 = Label(text="Username", font=("", 12))
        title2.pack()
        self.username_entry = Entry(background=self.theme["bg2"], justify="center", font=("", 12))
        self.username_entry.pack()
        self.username_entry.bind("<Return>", self.set_filled_in)
        title3 = Label(text="Password", font=("", 12))
        title3.pack()
        self.password_entry = Entry(background=self.theme["bg2"], justify="center", show="*", font=("", 12))
        self.password_entry.pack()
        self.password_entry.bind("<Return>", self.set_filled_in)
        Label().pack()
        connect_button = Button(text="Join", command=lambda: self.set_server(self.server_entry.get(), self.username_entry.get(), self.password_entry.get()), background=self.theme["bg2"], font=("", 12))
        connect_button.pack()

        self.logon_win.mainloop()

    def set_filled_in(self, *args):
        if self.server_entry.get() != "" and self.username_entry.get() != "" and self.password_entry.get() != "":
            self.set_server(self.server_entry.get(), self.username_entry.get(), self.password_entry.get())

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
        self.root.geometry("900x500")
        self.root.resizable(False, False)

        self.root.tk_setPalette(background=self.theme["bg"], foreground=self.theme["fg"],
               activeBackground=self.theme["bg2"], activeForeground=self.theme["fg"])

        self.messages = Listbox(width=80, height=15, font=("", 12), bg=self.theme["bg2"], selectbackground=self.theme["bg2"], selectforeground=self.theme["fg"])
        self.messages.grid(pady=(25,15))
        self.messages.bind('<Double-1>', self.onselect)
        self.insert_system_message("Welcome to PyChat!")

        self.userlist = Listbox(width=22, height=15, font=("", 12), bg=self.theme["bg2"])
        self.userlist.grid(row=0, column=1, pady=(25,15))
        self.userlist.bind('<Double-1>', self.on_user_select)

        self.messagebox_var = StringVar()
        self.messagebox = Entry(textvariable=self.messagebox_var, width=35, font=("", 12))
        self.messagebox.bind("<Return>", self.send)
        self.messagebox.focus_set()
        self.messagebox.grid()

        self.send_message_button = Button(text="Send", font=("", 12), command=self.send, bg=self.theme["bg2"], width=13, height=1)
        self.send_message_button.grid(pady=(1, 1))

    def onselect(self, event):
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        self.root.clipboard_clear()
        self.root.clipboard_append(value)
        self.insert_system_message("Copied to clipboard.")

    def on_user_select(self, event):
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        self.messagebox.delete(0, END)
        self.messagebox.insert(0, "/dm " + value)

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
        send_command(self.s,{
            "command": "exit"
        })

        exit()

    def set_username(self, username):
        send_command(self.s,{
            "command": "set_username",
            "username": username
        })

        self.insert_command_response("username", [f"Set username to {username}"])
        self.username = username

    def request_online_users(self):
        send_command(self.s,{
            "command": "online_users",
            "manual_call": True
        })

    def request_users(self):
        send_command(self.s,{
            "command": "users"
        })

    def direct_message(self, args):
        if not " " in args:
            return False

        user, message = args.split(" ", 1)

        send_command(self.s,{
            "command": "dm",
            "recipient": user,
            "message": message
        })

        return True

    def login(self, args):
        self.password = sha256(args[1].strip().encode()).hexdigest()
        send_command(self.s,{
            "command": "login",
            "username": args[0],
            "password": self.password,
            "manual_call": True
        })

    def addrole(self, args):
        username, role = args.split(" ", 1)

        send_command(self.s,{
            "command": "addrole",
            "username": username,
            "role": role
        })

    def ban(self, args):
        send_command(self.s, {
            "command": "ban",
            "username": args.strip()
        })
    
    def delete_account(self, args):
        send_command(self.s, {
            "command": "delete_account",
            "username": args.strip()
        })

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
            elif command == "help":
                lines = [
                    "--------------------------------------------------------------------------------",
                    "Client Commands:",
                    "/username <username>  -  Changes your username",
                    "/users  -  Lists all users",
                    "/theme <theme name> -  Changes the UI color theme",
                    "/themes  -  Lists all available themes",
                    "/dm <user> <message>  -  Sends a direct message",
                    "/addrole <user> <role>  -  Adds a role to a user (admin required)",
                    "/delete_account <user>  -  Deletes a user account (admin required)",
                    "/ban <user>  -  Bans a user (admin required)",
                    "--------------------------------------------------------------------------------"
                ]

                for line in lines:
                    self.insert_system_message(line)
            
            elif command == "username":
                self.set_username(args)
            elif command in ["online_users", "online-users", "onlineusers"]:
                self.request_online_users()
            elif command == "users":
                self.request_users()
            elif command == "theme":
                if args and args in THEMES:
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
            elif command in ["addrole", "add_role", "add-role"]:
                self.addrole(args)
            elif command in ["delete_account", "delete-account", "deleteaccount"]:
                self.delete_account(args)
            elif command == "ban":
                self.ban(args)
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
                    if msg['author']['username'] != self.username and f"@{self.username}" in msg["message"]:
                        playsound("resources/notif_sound.mp3", block=False)

                elif msg["command"] == "server_message":
                    self.insert_system_message(f"[SERVER] {msg['message']}")

                elif msg["command"] == "dm":
                    self.insert_message(f"[DM] {msg['author']['username']}: {msg['message']}")
                    if msg['author']['username'] != self.username:
                        playsound("resources/notif_sound.mp3", block=False)

                elif msg["command"] == "user_join":
                    self.insert_system_message(f"> {msg['user']} {choice(self.JOIN_MESSAGES)}")

                elif msg["command"] == "user_leave":
                    self.insert_system_message(f"< {msg['user']} {choice(self.LEAVE_MESSAGES)}")

                elif msg["command"] == "online_users":
                    if msg["manual_call"]:
                        self.insert_command_response("users", [user["username"] for user in msg["users"]])

                    self.userlist.delete(0,END)
                    for user in msg["users"]:
                        self.userlist.insert(END, f"{user['username']}{' (admin)' if 'admin' in user['roles'] else ''}")

                elif msg["command"] == "users":
                    msgs = []
                    for user in msg["users"]:
                        msgs.append(f"{user['username']} [{'ONLINE' if user['online'] else 'OFFLINE'}]{' (admin)' if 'admin' in user['roles'] else ''}")
                    self.insert_command_response("users", msgs)

                elif msg["command"] == "banned":
                    self.insert_system_message("You have been banned from this server.")
                elif msg["command"] == "kicked":
                    self.insert_system_message("You have been kicked from this server.")

                # result messages
                
                elif msg["command"] == "login_result":
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
                
                elif msg["command"] == "addrole_result":
                    if msg["result"] == "invalid_user":
                        self.insert_command_response("addrole", ["Invalid user"])
                    elif msg["result"] == "insufficient_perms":
                        self.insert_command_response("addrole", ["Insufficient permissions. Make sure you are a server admin.", "If you own this server, change ADMIN_USERID in lib/server.py to your id."])
                    elif msg["result"] == "success":
                        self.insert_command_response("addrole", ["Role added"])
                
                elif msg["command"] in ["delete_account_result", "delete_account_result"]:
                    if msg["result"] == "insufficient_perms":
                        self.insert_command_response("delete_account", ["Insufficient permissions - you need the admin role to use this command"])
                    elif msg["result"] == "invalid_user":
                        self.insert_command_response("delete_account", ["Invalid user"])
                    elif msg["result"] == "success":
                        self.insert_command_response("delete_account", [f"Account deleted"])
                
                elif msg["command"] in ["ban_result", "ban_result"]:
                    if msg["result"] == "insufficient_perms":
                        self.insert_command_response("ban", ["Insufficient permissions - you need the admin role to use this command"])
                    elif msg["result"] == "invalid_user":
                        self.insert_command_response("ban", ["Invalid user"])
                    elif msg["result"] == "user_offline":
                        self.insert_command_response("ban", ["Invalid user - user needs to be online for ip ban"])
                    elif msg["result"] == "success":
                        self.insert_command_response("ban", [f"Successfully ip banned the user"])
