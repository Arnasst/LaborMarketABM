import logging

from openai import OpenAI

from random import seed
from numpy.random import seed as np_seed

from labor_model.config import Settings
from labor_model.local_logging import logger
from labor_model.model import LaborModel
from labor_model.stats import StepStatsCalculator, print_company_stats, print_employee_stats, print_unemployment_stats


def main():
    logger.setLevel(logging.WARNING)
    settings = Settings()

    # To fix the results
    # seed(1)
    # np_seed(1)

    NUM_EMPLOYEES = 95
    NUM_COMPANIES = 9
    # NUM_EMPLOYEES = 95
    # NUM_COMPANIES = 9
    llm_based = True
    open_ai_client = OpenAI(api_key=settings.open_ai_key) if llm_based else None
    model = LaborModel(NUM_EMPLOYEES, NUM_COMPANIES, settings, llm_based, open_ai_client)
    stats = StepStatsCalculator(model)

    MODEL_STEPS = 120
    for _ in range(MODEL_STEPS):
        model.step()
        stats.step()

    successful_parses = sum(company.parses_succeeded for company in model.companies)
    failed_parses = sum(company.parses_failed for company in model.companies)

    print(f"Failed parses {failed_parses / (successful_parses + failed_parses)} out of {successful_parses + failed_parses}")
    profits = stats.get_total_profits()
    print_company_stats(model.companies, profits)
    print(f"Unemployment rates: {stats.unemployment_rates}")

    print(f"Wage stats: {stats.wage_stats}")
    # print(f"Total funds: {stats.total_funds}")
    # print(f"Fill rates: {stats.product_fill_rates}")
    print_unemployment_stats(stats.unemployment_rates)
    print_employee_stats(model.employees)

    change_count = model.quit_count + model.fire_count
    print(f"Quit percentage: {model.quit_count / change_count:.2}")
    print(f"Fire percentage: {model.fire_count / change_count:.2}")


if __name__ == "__main__":
    main()
