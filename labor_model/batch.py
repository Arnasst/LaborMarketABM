from itertools import groupby
import logging
from pprint import pprint
from mesa.batchrunner import batch_run

from labor_model.config import Settings
from labor_model.model import LaborModel
from labor_model.local_logging import logger

def calculate_group_statistics(groups: list[list[dict]]):
    statistics = []

    for group in groups:
        total_unemployment_rate = sum(item['Unemployment Rate'] for item in group)
        average_unemployment_rate = total_unemployment_rate / len(group)

        group_settings = group[0]['settings']
        group_info = {
            'num_companies': group[0]['num_companies'],
            'num_employees': group[0]['num_employees'],
            'initial_product_cost': group_settings.initial_product_cost,
            'base_operating_cost': group_settings.base_operating_cost,
            'cost_per_hire': group_settings.cost_per_hire,
            'initial_salary': group_settings.initial_salary,
            'changing_jobs_raise': group_settings.changing_jobs_raise,
            'initial_employment_rate': group_settings.initial_employment_rate,
            'quitting_multiplier': group_settings.quitting_multiplier,
            'average_unemployment_rate': average_unemployment_rate,
        }

        statistics.append(group_info)

    return statistics

def group_elements(data: list[dict]):
    def grouping_key(d):
        return tuple((k, d[k] if type(d[k]) is not Settings else list(d[k].model_dump().values())) for k in sorted(d) if k in ['num_companies', 'num_employees', 'settings'])

    sorted_data = sorted(data, key=grouping_key)

    grouped_data = []
    for key, group in groupby(sorted_data, key=grouping_key):
        grouped_data.append(list(group))

    return grouped_data


def form_all_setting_variations(settings: Settings) -> list[Settings]:
    setting_variations = []

    operating_cost_range = range(50, 70, 10)
    for i in operating_cost_range:
        new_setting = settings.model_copy()
        new_setting.base_operating_cost = i
        setting_variations.append(new_setting)

    return setting_variations

def main() -> None:
    logger.setLevel(logging.ERROR)

    settings = Settings()

    NUM_EMPLOYEES = 150

    setting_variations = form_all_setting_variations(settings)

    parameters = {
        "num_employees": NUM_EMPLOYEES,
        "num_companies": [10, 20],
        "settings": setting_variations,
        "llm_based": False,
        "open_ai_client": None
    }

    results = batch_run(
        model_cls=LaborModel,
        parameters=parameters,
        number_processes=None,
        iterations=2,
        max_steps=60,
        display_progress=True
    )

    grouped_results = group_elements(results)
    group_stats = calculate_group_statistics(grouped_results)
    pprint(group_stats)

if __name__ == "__main__":
    main()
