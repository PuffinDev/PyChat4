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
    usernames = []
    for client in clients:
        if not client.user:
            continue
        usernames.append(client.user.username)

    return {
        "command": "online_users",
        "users": usernames,
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
        "users": users,
    }

def direct_message(author, message):
    return {
        "command": "dm",
        "author": author,
        "message": message
    }

def result_message(result, manual_call=False):
    return {
        "command": "result",
        "result": result,
        "manual_call": manual_call
    }