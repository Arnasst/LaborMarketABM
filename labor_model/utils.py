from random import random

AVERAGE_PRODUCTIVITY = 5

INFLATION_RATE = 0.03

JOBS_TO_EMPLOYEES_RATIO = 1.06


def decide_based_on_probability(probability: int) -> bool:
    return random() < probability
