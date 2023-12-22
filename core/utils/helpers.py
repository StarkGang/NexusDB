import random
import time


def generate_unique_5_digit_number():
    timestamp = int(time.time() * 1000)
    random_suffix = random.randint(0, 99999)
    return (timestamp % 100000) * 100000 + random_suffix
