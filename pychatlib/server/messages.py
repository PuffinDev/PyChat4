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
