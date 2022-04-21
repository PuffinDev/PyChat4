# PyChat4
PyChat is a feature rich, lightweight and customisable chatroom software written in python.

<img src="screenshots/pychat4.png" width="60%" height="60%">

## Features

- Easy to set up and customise server
- Official server running 24/7
- Hackable codebase - make your own bots, clients and more!
- Direct messages and user accounts
- Many /commands to try out
- Ping members and roles
- Administration tools such as /ban and /kick
- Customisable client themes

## Get started

### Run the following commands to get started and connect to the official server:

`git clone https://github.com/PuffinDev/PyChat4/`

`cd PyChat4`

`python3 -m pip install -r requirements.txt`

`python3 client.py`

Choose a username and password, and click connect.

For info on commands, type `/help` into the chat

<br>

### Run the following commands to run your own server:

`git clone https://github.com/PuffinDev/PyChat4 && cd PyChat4` (only run if you don't yet have pychat downloaded!)

`python3 server.py`

If you want to connect to your server from outside your local network, forward port 8888 on your router.

## Customise

### Theming

Themes are stored in `client/config.py` in the `THEMES` list. To add a theme, just add a python dict containing your chosen hex colors.

Example:

```py
"void": {
    "bg": "#000000",
    "bg2": "#000000",
    "fg": "#57B1FF",
    "fg_highlight": "#87B5E4"
},
```

### Bots

Creating a PyChat bot is extremely simple, thanks to https://github.com/PuffinDev/PyChatBot - a library for writing pychat bots.
Bots have access to all the functionality that normal clients have access to such as DMs, roles, administration etc.
Check out the documentation for more info.

### Custom servers

The pychat protocol is designed to be hackable, so the official server code can easily be edited to behave however you want. You can add features such as auto-moderation and nicknames just my changing how information is handled on the server.

## Contributing

Any contributions are **greatly appreciated**, whether it's a simple UI change, or a huge protocol overhaul. Feel free to make a pull request!

## Community

If you want to get involved with developing or testing pychat, I highly recommend you join the discord: https://discord.gg/RVba4BkQ5K
