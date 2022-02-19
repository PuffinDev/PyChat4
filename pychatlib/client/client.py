import socket
import json
from threading import Thread
from random import choice
from tkinter import *

from .networking import receive, send_message, send_command
from .themes import THEMES

class Client:
    def __init__(self):
        self.JOIN_MESSAGES = ["just joined!", "has joined", "has entered the chat", "arrived!", "slid in!", "showed up!", "joined the party!"]
        self.LEAVE_MESSAGES = ["left the chat", "has left", "just left", "has exited", "flew away!"]
        self.THEME = THEMES["sweden"]

        self.init_gui()
        self.init_socket()
        self.gui_mainloop()

    def init_gui(self):
        self.root = Tk()
        self.root.title("PyChat4")
        self.root.geometry("600x350")

        self.root.tk_setPalette(background=self.THEME["bg"], foreground=self.THEME["fg"],
               activeBackground=self.THEME["bg2"], activeForeground=self.THEME["fg"])

        self.messages = Listbox(width=90, height=10, font=("", 11), bg=self.THEME["bg2"])
        self.messages.pack(pady=(25,15))
        self.insert_message("Welcome to PyChat!")

        self.messagebox_var = StringVar()
        self.messagebox = Entry(textvariable=self.messagebox_var)
        self.messagebox.pack()

        self.send_message_button = Button(text="Send", font=("", 12), command=self.send, bg=self.THEME["bg2"])
        self.send_message_button.pack(pady=(5, 5))

    def set_gui_theme(self):
        self.root.tk_setPalette(background=self.THEME["bg"], foreground=self.THEME["fg"],
               activeBackground=self.THEME["bg2"], activeForeground=self.THEME["fg"])
        
        self.messages.config(bg=self.THEME["bg2"])
        self.send_message_button.config(bg=self.THEME["bg2"])

    def gui_mainloop(self):
        self.root.mainloop()

    def init_socket(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(("0.0.0.0", 5555))

        thread = Thread(target=self.receive_loop, daemon=True)
        thread.start()

    def insert_message(self, msg):
        self.messages.insert(END, f"{msg}")
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

    def log(self, msg):
        self.insert_message(f"[CLIENT] {msg}")

    def send(self):
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
            elif command == "theme":
                if args in THEMES:
                    self.THEME = THEMES[args]
                    self.set_gui_theme()
                    self.log(f"Set theme to {args}")
                else:
                    self.log(f"That is not a valid theme. Use /themes to see them")
            elif command == "themes":
                msg = "Themes: "
                for i, theme in enumerate(THEMES):
                    if i == 0:
                        msg += f"{theme}"
                    else:
                        msg += f", {theme}"
                
                self.log(msg)
            else:
                self.log("That is not a valid command!")

        self.messagebox_var.set("")


    def receive_loop(self):
        while True:
            msg = receive(self.s)
            if not msg:
                continue

            if msg["command"] == "message":
                self.insert_message(f"{msg['author']['username']}: {msg['message']}")
            
            elif msg["command"] == "user_join":
                self.insert_message(f"> {msg['user']} {choice(self.JOIN_MESSAGES)}")
            
            elif msg["command"] == "user_leave":
                self.insert_message(f"< {msg['user']} {choice(self.LEAVE_MESSAGES)}")
