class Client:
    def __init__(self, conn, addr, _id, username="Guest"):
        self.connection = conn
        self.address = addr
        self.id = _id
        self.username = username

    def json(self):
        return {
            "id": self.id,
            "username": self.username,
            "address": self.address
        }
