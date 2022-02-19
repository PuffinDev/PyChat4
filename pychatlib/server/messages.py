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

def users_message(clients):
    usernames = []
    for client in clients:
        usernames.append(client.username)
    
    return {
        "command": "users",
        "users": usernames
    }