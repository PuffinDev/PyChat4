import socket
import json
from threading import Thread
from random import choice
from tkinter import *

from .networking import receive, send_message, send_command

class Client:
    def __init__(self):
        self.JOIN_MESSAGES = ["just joined!", "has joined", "has entered the chat", "arrived!", "slid in!", "showed up!", "joined the party!"]
        self.LEAVE_MESSAGES = ["left the chat", "has left", "just left", "has exited", "flew away!"]

        self.init_gui()
        self.init_socket()
        self.gui_mainloop()

    def init_gui(self):
        self.root = Tk()
        self.root.title("PyChat4")

        self.title = Label(text="PyChat4", font=("", 15))
        self.title.pack()

        self.messages = Listbox()
        self.messages.pack()

        self.messagebox_var = StringVar()
        self.messagebox = Entry(textvariable=self.messagebox_var)
        self.messagebox.pack()

        self.send_message_button = Button(text="Send", font=("", 12), command=self.send)
        self.send_message_button.pack()

    def gui_mainloop(self):
        self.root.mainloop()

    def init_socket(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(("0.0.0.0", 5555))

        thread = Thread(target=self.receive_loop, daemon=True)
        thread.start()

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

    def log(msg):
        self.messagebox.insert(END, f"[CLIENT] {msg}")

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
            if command == "username":
                self.set_username(args)
            else:
                log("That is not a valid command!")

        self.messagebox_var.set("")


    def receive_loop(self):
        while True:
            msg = receive(self.s)
            if not msg:
                continue

            if msg["command"] == "message":
                self.messages.insert(END, f"{msg['author']['username']}: {msg['message']}")
            
            elif msg["command"] == "user_join":
                self.messages.insert(END, f"> {msg['user']} {choice(self.JOIN_MESSAGES)}")
            
            elif msg["command"] == "user_leave":
                self.messages.insert(END, f"< {msg['user']} {choice(self.LEAVE_MESSAGES)}")
