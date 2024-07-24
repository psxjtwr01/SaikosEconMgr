import json
import os
import random
from datetime import datetime, timedelta

# Command cooldowns
cooldowns = {
    "bal": timedelta(seconds=5),
    "work": timedelta(hours=1),
    "rob": timedelta(minutes=2),
    "lvl": timedelta(seconds=5),
    "esex": timedelta(hours=2),
    "gamble": timedelta(seconds=10),
    "cd": timedelta(seconds=10)
}

def load_data():
    if os.path.exists("economy_data.json"):
        with open("economy_data.json", "r") as file:
            return json.load(file)
    else:
        return {}

def save_data(data):
    with open("economy_data.json", "w") as file:
        json.dump(data, file)

def gamble(user_id, amount_str):
    data = load_data()
    try:
        amount = int(amount_str)
    except ValueError:
        return "Please provide a valid amount to gamble."

    if amount <= 0:
        return "You need to gamble a positive amount."

    user_balance = data.setdefault(str(user_id), {"balance": 0})["balance"]
    if amount > user_balance:
        return "You don't have enough money to gamble that amount."

    win = random.random() < 0.3
    if win:
        winnings = amount * 2
        data[str(user_id)]["balance"] += winnings
        result = f"Congratulations, you won ${winnings}!"
    else:
        data[str(user_id)]["balance"] -= amount
        result = f"Sorry, you lost ${amount}. Better luck next time!"

    save_data(data)
    return result

def get_balance(user_id):
    data = load_data()
    balance = data.get(str(user_id), {}).get("balance", 0)
    level = data.get(str(user_id), {}).get("level", 1)
    return f"Your balance is ${balance} and your level is {level}"

def work(user_id):
    data = load_data()
    user_data = data.setdefault(str(user_id), {"balance": 0, "level": 1})
    user_data[str(user_id)]["level"] += 0.25 * user_data[str(user_id)]["level"]
    earnings = random.randint(1, 600) * user_data["level"]
    user_data["balance"] += earnings
    save_data(data)
    return f"You worked and earned ${earnings}"

def rob(user_id, target_id):
    data = load_data()
    if random.random() < 0.25:
        target_data = data.get(str(target_id), {"balance": 0})
        stolen_amount = random.randint(1, min(200, target_data["balance"]))
        if stolen_amount > 0:
            target_data["balance"] -= stolen_amount
            data[str(user_id)]["balance"] += stolen_amount
            result = f"Successfully robbed {stolen_amount}"
        else:
            result = "Tried to rob, but they had no money to steal!"
    else:
        result = "Failed to rob"

    save_data(data)
    return result

# For debugging purposes
