class Client:
    def __init__(self, conn, addr, _id):
        self.connection = conn
        self.address = addr
        self.id = _id
        self.user = None

    def json(self):
        return {
            "id": self.id,
            "username": self.username,
            "address": self.address
        }

class User:
    def __init__(self):
        pass

    def json(self):
        return {
            "username": self.username,
            "password": self.password,
            "id": self.id
        }

    def info_json(self):
        return {
            "username": self.username,
            "id": self.id
        }

    def from_json(self, user_json):
        self.username = user_json["username"]
        self.password = user_json["password"]
        self.id = user_json["id"]
        return self