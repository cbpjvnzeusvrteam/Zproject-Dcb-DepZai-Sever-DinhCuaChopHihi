import os
import json

def load_user_memory(user_id):
    path = f"memory_{user_id}.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_user_memory(user_id, history):
    path = f"memory_{user_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history[-10:], f, ensure_ascii=False, indent=2)

def load_groups():
    if os.path.exists("groups.json"):
        with open("groups.json", "r") as f:
            return set(json.load(f))
    return set()

def save_groups(groups):
    with open("groups.json", "w") as f:
        json.dump(list(groups), f)