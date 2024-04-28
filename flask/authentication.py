import database as db

def login(username, password):
    error_message = "Invalid username or password. Please try again."
    if not username or not password:
        return False, error_message

    user = db.get_user(username)
    if user is None or user["password"] != password:
        return False, error_message

    user_info = {
        "username": username,
        "first_name": user["first_name"],
        "last_name": user["last_name"]
    }
    return True, user_info
