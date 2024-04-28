import logging

from openai import OpenAI

from labor_model.config import Settings
from labor_model.local_logging import logger
from labor_model.model import LaborModel
from labor_model.stats import StepStatsCalculator, print_employee_stats


def main():
    logger.setLevel(logging.WARNING)
    settings = Settings()

    NUM_EMPLOYEES = 100
    NUM_COMPANIES = 10
    llm_based = False
    open_ai_client = OpenAI(settings.open_ai_key) if llm_based else None
    model = LaborModel(NUM_EMPLOYEES, NUM_COMPANIES, llm_based, open_ai_client)
    stats = StepStatsCalculator(model)

    MODEL_STEPS = 60
    for _ in range(MODEL_STEPS):
        model.step()
        stats.step()

    print(f"Unemployment rates: {stats.unemployment_rates}")
    unemployment_average = sum(stats.unemployment_rates) / len(stats.unemployment_rates)
    unemployment_deviation = sum((rate - unemployment_average) ** 2 for rate in stats.unemployment_rates) / len(stats.unemployment_rates)
    print(f"Unemployment average: {unemployment_average:.2}")
    print(f"Unemployment deviation: {unemployment_deviation:.2}")
    # print(f"Wage stats: {stats.wage_stats}")
    # print(f"Total funds: {stats.total_funds}")
    # print(f"Fill rates: {stats.product_fill_rates}")
    # print_employee_stats(model.employees)


if __name__ == "__main__":
    main()

# Įdomu, kad daugiau mažų kompanijų - mažesnis nedarbo lygis.
