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

def users_message(clients, manual_call=False):
    usernames = []
    for client in clients:
        usernames.append(client.user.username)

    return {
        "command": "users",
        "users": usernames,
        "manual_call": manual_call
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