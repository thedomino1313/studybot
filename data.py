import json
import os

def read_users():
    if os.path.exists("./assets/users.json"):
        return json.load(open("./assets/users.json"))
    else:
        return dict()

def browse():
    return os.listdir("./assets/quizzes")

def get_answers(file: str):
    path = f"./assets/quizzes/{file}/answers.txt"
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read().strip().split("\n")
    return []

def get_selection(user:str):
    return get_user(user)["selection"]

def make_new_data():
    data = dict()
    data["selection"] = None
    data["quizid"] = [None, None]
    data["quizzes"] = dict()
    for quiz in browse():
        data["quizzes"][quiz] = [""] * len(get_answers(quiz))
    return data

def get_user(user:str) -> dict:
    users = read_users()
    if user in users: return users[user]
    else: return make_new_data()

def write_user(user:str, user_data:dict):
    users = read_users()
    users[user] = user_data
    with open("./assets/users.json", 'w') as f:
        json.dump(users, f)

def get_users() ->list:
    return list(read_users().keys())

def add_test(name):
    data = read_users()
    num = len(get_answers(name))
    for user in data:
        data[user]["quizzes"][name] = [""] * num
    with open("./assets/users.json", 'w') as f:
        json.dump(data, f)

def update_tests():
    data = read_users()
    items = browse()
    nums = {item: len(get_answers(item)) for item in items}
    for user in data:
        for item in items:
            if item not in data[user]["quizzes"] or len(data[user]["quizzes"][item]) != nums[item]:
                data[user]["quizzes"][item] = [""] * nums[item]
    with open("./assets/users.json", 'w') as f:
        json.dump(data, f)

if __name__ == "__main__":
    write_user("test", get_user("test"))