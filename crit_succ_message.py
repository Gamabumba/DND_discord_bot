import random

crit_fail_messages = [
    "ГООООООЛ!",
    "Выпал крит - Джекпот!",
    "Мортред всех ебёт!",
    "Нагиб 228!",
    "Скилл вери вери хай, инвокером играть в кайф!"
]


def get_random_crit_message():
    return random.choice(crit_fail_messages)
