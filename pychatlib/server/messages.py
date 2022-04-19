def leave_message(user):
    return {
        "command": "user_leave",
        "user": user
    }

def join_message(user):
    return {
        "command": "user_join",
        "user": user
    }

def online_users_message(clients, manual_call=False):
    users = []
    for client in clients:
        if not client.user:
            continue
        users.append(client.user.info_json())

    return {
        "command": "online_users",
        "users": users,
        "manual_call": manual_call
    }

def users_message(clients, full_users):
    users = []
    user_ids = []

    for client in clients:
        if client.user:
            json = client.user.info_json()
            json["online"] = True
            users.append(json)
            user_ids.append(json["id"])

    for user in full_users:
        json = user.info_json()
        if user.id in user_ids:
            continue

        json["online"] = False
        users.append(json)

    return {
        "command": "users",
        "users": users
    }

def direct_message(author, message):
    return {
        "command": "dm",
        "author": author,
        "message": message
    }

def result_message(command, result, manual_call=False):
    return {
        "command": f"{command}_result",
        "result": result,
        "manual_call": manual_call
    }

def custom_result_message(command, result_message):
    return {
        "command": "custom_result",
        "responding_to": command,
        "result_message": result_message
    }


def server_message(message):
    return {
        "command": "server_message",
        "message": message
    }

def banned_message():
    return {"command": "banned"}
