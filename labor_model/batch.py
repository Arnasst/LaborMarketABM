from itertools import groupby
import logging
from pprint import pprint
from mesa.batchrunner import batch_run

from labor_model.config import Settings
from labor_model.model import LaborModel
from labor_model.local_logging import logger

def sort_closest_groups(groups: list[list[dict]]):
    EXPECTED_UNEMPLOYMENT = 0.067
    AVERAGE_TENURE = 29
    TIME_BETWEEN_JOBS = 2
    CHANGE_REASON_QUIT = 0.6

    def calculate_error(group: dict) -> float:
        unemployment_error = abs(group['average_unemployment_rate'] - EXPECTED_UNEMPLOYMENT) / EXPECTED_UNEMPLOYMENT
        tenure_error = abs(group['average_work_tenure'] - AVERAGE_TENURE) / AVERAGE_TENURE
        time_between_jobs_error = abs(group['average_time_between_jobs'] - TIME_BETWEEN_JOBS) / TIME_BETWEEN_JOBS
        quit_error = abs(group['average_quit_rate'] - CHANGE_REASON_QUIT) / CHANGE_REASON_QUIT

        return unemployment_error + tenure_error + time_between_jobs_error + quit_error

    sorted_groups = sorted(groups, key=calculate_error)

    return sorted_groups

def calculate_group_statistics(groups: list[list[dict]]):
    statistics = []

    for group in groups:
        total_unemployment_rate = sum(item['Unemployment Rate'] for item in group)
        average_unemployment_rate = round(total_unemployment_rate / len(group), 2)

        total_profits = sum(item['Company Profit Average'] for item in group)
        average_profits = round(total_profits / len(group), 2)

        total_tenure = sum(item['Average Work Tenure'] for item in group)
        average_tenure = round(total_tenure / len(group), 2)

        total_time_between_jobs = sum(item['Average Time Between Jobs'] for item in group)
        average_time_between_jobs = round(total_time_between_jobs / len(group), 2)

        total_average_quit_rate = sum(item['Average Quit Rate'] for item in group)
        average_quit_rate = round(total_average_quit_rate / len(group), 2)

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
            "average_work_tenure": average_tenure,
            "average_time_between_jobs": average_time_between_jobs,
            "average_quit_rate": average_quit_rate,
            # "average_company_profits": average_profits
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

    operating_cost_range = range(100, 201, 50)
    for i in operating_cost_range:
        new_setting = settings.model_copy()
        new_setting.base_operating_cost = i

        quitting_multiplier_range = range(2, 10, 3) # Divided later by 10
        for i in quitting_multiplier_range:
            new_setting = settings.model_copy()
            new_setting.quitting_multiplier = i / 10

            product_cost_range = range(200, 250, 10)
            for i in product_cost_range:
                new_setting = settings.model_copy()
                new_setting.initial_product_cost = i
                setting_variations.append(new_setting)

    return setting_variations

def main() -> None:
    logger.setLevel(logging.ERROR)

    settings = Settings()

    setting_variations = form_all_setting_variations(settings)

    parameters = {
        "num_employees": range(50, 150, 10),
        "num_companies": range(10, 20),
        "settings": setting_variations,
        "llm_based": False,
        "open_ai_client": None
    }

    results = batch_run(
        model_cls=LaborModel,
        parameters=parameters,
        number_processes=None,
        iterations=10,
        max_steps=60,
        display_progress=True
    )

    grouped_results = group_elements(results)
    group_stats = calculate_group_statistics(grouped_results)
    filtered_groups = sort_closest_groups(group_stats)[:5]
    pprint(filtered_groups)

if __name__ == "__main__":
    main()
