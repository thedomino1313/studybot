from data import *

def get_data(func):
    def get_user_data(user, *args, **kwargs) -> str:
        user_data = get_user(user)
        if user_data["selection"] == None:
            write_user(user, user_data)
            return "Please select a quiz first!"
        else:
            return func(user, *args, user_data, **kwargs)
    return get_user_data

def get_current_guesses(user_data: dict) -> list[str]:
    return user_data["quizzes"][user_data["selection"]] if user_data["selection"] else []

def set_current_guesses(user_data: dict, guesses: list[str]) -> dict:
    if user_data["selection"]:
        user_data["quizzes"][user_data["selection"]] = guesses
        return user_data
    else:
        return []

def get_remaining_words(user_data: dict) -> list[str]:
    return list(filter(lambda x: x not in get_current_guesses(user_data), get_answers(user_data["selection"])))

def get_score(user_data: dict, intermediate:bool=True) -> str:
    if intermediate:
        return f"{sum(int(x == y) for x,y in zip(get_current_guesses(user_data), get_answers(user_data['selection'])))}/{len([x for x in get_current_guesses(user_data) if x != ''])}"
    return f"{sum(int(x == y) for x,y in zip(get_current_guesses(user_data), get_answers(user_data['selection'])))}/{len(get_current_guesses(user_data))}"

def select(user:str, selection:str) -> tuple:
    user_data = get_user(user)
    if selection in browse():
        if user_data["selection"] == selection:
            return f"{selection} is already selected!"
        user_data["selection"] = selection
        write_user(user, user_data)
        return f"{selection} has been selected!"
    return "Selection does not exist!"

@get_data
def guess_term(user:str, number:int, guess:str, user_data:dict=None) -> tuple:
    if len((guesses := get_current_guesses(user_data))) >= (number_modified := number - 1):
        if guess in get_answers(user_data["selection"]):
            guesses[number_modified] = guess
            write_user(user, set_current_guesses(user_data, guesses))
            return f"{guess} has been placed in slot {number}!"
        else: return f"There is no term `{guess}`"
    else: return f"There is no space numbered {number}."

@get_data
def clear(user:str, user_data:dict=None, number:int=None):
    if number == None:
        write_user(user, set_current_guesses(user_data, [""]*len(get_current_guesses(user_data))))
        return "All slots cleared!"
    else:
        if len((guesses := get_current_guesses(user_data))) >= (number_modified := number - 1):
            guesses[number_modified] = ""
            write_user(user, set_current_guesses(user_data, guesses))
            return f"Slot {number} cleared!"
        else: return f"There is no space numbered {number}."

@get_data
def evaluate_score(_:str, user_data:dict=None, intermediate:bool=True) -> str:
    if intermediate:
        return f"Current score: {get_score(user_data, intermediate)}!"
    return f"Your score is {get_score(user_data, intermediate)}!"

@get_data
def format_guesses(_:str, user_data:dict=None):
    guesses = get_current_guesses(user_data)
    underscores = '\_' * max([5] + [len(x) for x in guesses])
    return [f"{i + 1:02}: {guess if guess else underscores}" for i, guess in enumerate(guesses)]

if __name__ == "__main__":
    user = "test"
    select(user, "skull1")
    print(guess_term(user, 'Coronal suture', 1))
    print(evaluate_score(user, intermediate=True))
    print(evaluate_score(user, intermediate=False))
    print(get_user(user))