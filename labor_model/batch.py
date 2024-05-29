from itertools import groupby
import logging
from pprint import pprint
from mesa.batchrunner import batch_run

from labor_model.config import Settings
from labor_model.model import LaborModel
from labor_model.local_logging import logger

EXPECTED_UNEMPLOYMENT = 0.067
AVERAGE_TENURE = 29
TIME_BETWEEN_JOBS = 2
# CHANGE_REASON_QUIT = 0.65

def calculate_group_error(group: dict) -> float:
    unemployment_error = abs(group['average_unemployment_rate'] - EXPECTED_UNEMPLOYMENT) / EXPECTED_UNEMPLOYMENT
    tenure_error = abs(group['average_work_tenure'] - AVERAGE_TENURE) / AVERAGE_TENURE
    time_between_jobs_error = abs(group['average_time_between_jobs'] - TIME_BETWEEN_JOBS) / TIME_BETWEEN_JOBS
    # quit_error = abs(group['average_quit_rate'] - CHANGE_REASON_QUIT) / CHANGE_REASON_QUIT

    return unemployment_error + tenure_error + time_between_jobs_error

def sort_closest_groups(groups: list[list[dict]]):
    sorted_groups = sorted(groups, key=calculate_group_error)

    return sorted_groups

def calculate_group_statistics(groups: list[list[dict]]):
    statistics = []

    for group in groups:
        total_unemployment_rate = sum(item['Unemployment Rate'] for item in group)
        average_unemployment_rate = round(total_unemployment_rate / len(group), 3)

        total_profits = sum(item['Company Profit Average'] for item in group)
        average_profits = round(total_profits / len(group), 2)

        total_tenure = sum(item['Average Work Tenure'] for item in group)
        average_tenure = round(total_tenure / len(group), 2)

        total_time_between_jobs = sum(item['Average Time Between Jobs'] for item in group)
        average_time_between_jobs = round(total_time_between_jobs / len(group), 2)

        total_average_quit_rate = sum(item['Average Quit Rate'] for item in group)
        average_quit_rate = round(total_average_quit_rate / len(group), 2)

        total_original_companies_left = sum(item['Original Companies Left'] for item in group)
        average_original_companies_left = round(total_original_companies_left / len(group), 2)

        total_original_companies_profits = sum(item['Original Company Profits'] for item in group)
        average_original_companies_profits = round(total_original_companies_profits / len(group), 2)

        group_settings = group[0]['settings']
        group_info = {
            'num_companies': group[0]['num_companies'],
            'num_employees': group[0]['num_employees'],
            'initial_product_cost': group_settings.initial_product_cost,
            'base_operating_cost': group_settings.base_operating_cost,
            'cost_per_hire': group_settings.cost_per_hire,
            # 'initial_salary': group_settings.initial_salary,
            # 'changing_jobs_raise': group_settings.changing_jobs_raise,
            # 'initial_employment_rate': group_settings.initial_employment_rate,
            'quitting_multiplier': group_settings.quitting_multiplier,
            'average_unemployment_rate': average_unemployment_rate,
            "average_work_tenure": average_tenure,
            "average_time_between_jobs": average_time_between_jobs,
            "average_quit_rate": average_quit_rate,
            "average_company_profits": average_profits,
            "average_companies_left": average_original_companies_left,
            "average_original_companies_profits": average_original_companies_profits,
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

    # operating_cost_range = range(70, 90, 3)
    # for i in operating_cost_range:
    #     i_setting = settings.model_copy()
    #     i_setting.base_operating_cost = i

    quitting_multiplier_range = range(20, 30, 1) # Divided later by 100
    for i in quitting_multiplier_range:
        i_setting = settings.model_copy()
        i_setting.quitting_multiplier = i / 100
        setting_variations.append(i_setting)

        # firing_prob_range = range(5, 50, 5)
        # for j in firing_prob_range:
        #     j_setting = i_setting.model_copy()
        #     j_setting.company_fire_probability = j / 100

        #     emergency_months_range = range(10, 30, 2) # Divided later by 10
        #     for k in emergency_months_range:
        #         k_setting = j_setting.model_copy()
        #         k_setting.company_emergency_months = k / 10
        #         setting_variations.append(k_setting)

    # product_cost_range = range(220, 230, 2)
    # for z in product_cost_range:
    #     z_setting = y_setting.model_copy()
    #     z_setting.initial_product_cost = z

    #     hiring_cost_range = range(1300, 1700, 100)
    #     for x in hiring_cost_range:
    #         x_setting = z_setting.model_copy()
    #         x_setting.cost_per_hire = x
    #         setting_variations.append(x_setting)

    return setting_variations

def main() -> None:
    logger.setLevel(logging.ERROR)

    settings = Settings()

    setting_variations = form_all_setting_variations(settings)

    parameters = {
        "num_employees": 95,
        "num_companies": 9,
        "settings": setting_variations,
        "llm_based": False,
        "open_ai_client": None
    }

    results = batch_run(
        model_cls=LaborModel,
        parameters=parameters,
        number_processes=None,
        iterations=3,
        max_steps=120,
        display_progress=True
    )

    grouped_results = group_elements(results)
    group_stats = calculate_group_statistics(grouped_results)
    for group in group_stats:
        group["error"] = calculate_group_error(group)

    # Draw graph
    # iterations = range(1, len(group_stats) + 1)
    errors = [group["error"] for group in group_stats]
    print(errors)

    import matplotlib.pyplot as plt
    plt.plot(errors)
    plt.xlabel("Iteration")
    plt.ylabel("Error")
    plt.title("Error vs Iteration")
    plt.savefig("error_vs_iteration.png")
    plt.show()

    # filtered_groups = sort_closest_groups(group_stats)[:5]
    # pprint(filtered_groups)

if __name__ == "__main__":
    main()
