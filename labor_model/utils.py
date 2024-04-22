from random import random

INITIAL_PRODUCT_COST = 220
COST_PER_HIRE = 2000
INITIAL_SALARY = 1000

AVERAGE_PRODUCTIVITY = 5
CHANGING_JOBS_RAISE = 1.15

INFLATION_RATE = 0.03

JOBS_TO_EMPLOYEES_RATIO = 1.06
INITIAL_EMPLOYMENT_RATE = 0.8


def decide_based_on_probability(probability: int) -> bool:
    return random() < probability
