from dataclasses import dataclass

from labor_model.employee_agent import EmployeeAgent, WorkRecord
from labor_model.model import LaborModel


@dataclass
class Statistic:
    average: float
    median: float
    max: float
    min: float


class StepStatsCalculator:
    model: LaborModel
    unemployment_rates: list[float]
    wage_stats: list[Statistic]

    def __init__(self, model: LaborModel):
        self.model = model

        self.unemployment_rates = []
        self.wage_stats = []
        self.company_funds = []
        self.total_funds = []
        self.product_fill_rates = []

    def step(self):
        unemployment_rate = round(self.calculate_unemployment_rate(), 3)
        self.unemployment_rates.append(unemployment_rate)

        wage_stats = self.calculate_wage_stats()
        self.wage_stats.append(wage_stats)

        company_funds = self.get_company_funds()
        self.company_funds.append(company_funds)

        total_funds = round(sum(company_funds))
        self.total_funds.append(total_funds)

        product_fill_rates = round(self.get_companies_product_fill_rate(), 2)
        self.product_fill_rates.append(product_fill_rates)

    def calculate_unemployment_rate(self) -> float:
        return sum(1 for e in self.model.employees if not e.is_working) / len(
            self.model.employees
        )

    def calculate_wage_stats(self) -> Statistic | None:
        working_employees = [e for e in self.model.employees if e.is_working]
        if not working_employees:
            return None
        average_wage = sum(e.current_salary for e in working_employees) / len(
            working_employees
        )
        max_wage = max(e.current_salary for e in working_employees)
        min_wage = min(e.current_salary for e in working_employees)
        median_wage = sorted(e.current_salary for e in working_employees)[
            len(working_employees) // 2
        ]
        return Statistic(average_wage, median_wage, max_wage, min_wage)

    def get_company_funds(self) -> list[float]:
        return [c.funds for c in self.model.companies]

    def get_companies_product_fill_rate(self) -> float:
        return sum([c._calculate_total_productivity() / c.available_sellable_products_count for c in self.model.companies]) / len(self.model.companies)

def calculate_work_lengths(all_ended_work_records: list[WorkRecord]) -> list[int]:
    return [r.to_time - r.from_time for r in all_ended_work_records]


def calculate_time_between_jobs(
    all_employee_work_records: list[list[WorkRecord]],
) -> list[int]:
    times_between_jobs = []
    for work_records in all_employee_work_records:
        for i in range(len(work_records) - 1):
            times_between_jobs.append(
                work_records[i + 1].from_time - work_records[i].to_time
            )
    return times_between_jobs


def print_employee_stats(employees: list[EmployeeAgent]) -> None:
    all_employee_work_records = [e.work_records for e in employees]
    all_ended_work_records = [
        r
        for records in all_employee_work_records
        for r in records
        if r.to_time is not None
    ]
    work_lengths = calculate_work_lengths(all_ended_work_records)
    time_between_jobs = calculate_time_between_jobs(all_employee_work_records)
    print(f"Average work tenure: {sum(work_lengths) / len(work_lengths)}")
    print(f"Average time between jobs: {sum(time_between_jobs) / len(work_lengths)}")
