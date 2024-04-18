import logging

from labor_model.local_logging import logger
from labor_model.model import LaborModel
from labor_model.stats import StepStatsCalculator, print_employee_stats


def main():
    logger.setLevel(logging.INFO)

    NUM_EMPLOYEES = 10
    NUM_COMPANIES = 2
    model = LaborModel(NUM_EMPLOYEES, NUM_COMPANIES)
    stats = StepStatsCalculator(model)

    MODEL_STEPS = 15
    for _ in range(MODEL_STEPS):
        model.step()
        stats.step()

    print(f"Unemployment rates: {stats.unemployment_rates}")
    print(f"Wage stats: {stats.wage_stats}")
    # print_employee_stats(model.employees)


if __name__ == "__main__":
    main()

# Įdomu, kad daugiau mažų kompanijų - mažesnis nedarbo lygis.
