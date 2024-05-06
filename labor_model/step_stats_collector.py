from dataclasses import dataclass

from labor_model.employee_agent import EmployeeAgent, WorkRecord
from labor_model.company_agent import CompanyAgent
from mesa.datacollection import DataCollector
from mesa import Model


@dataclass
class Statistic:
    average: float
    median: float
    max: float
    min: float


class StepStatsCollector(DataCollector):
    model: Model
    unemployment_rates: list[float]
    wage_stats: list[Statistic]

    def __init__(self, model):
        super().__init__(
            model_reporters={
                "Unemployment Rate": lambda m: round(self.calculate_unemployment_rate(), 2),
                "Average Work Tenure": lambda m: round(self.calculate_average_tenure(), 2),
                # "Wage Stats": self.calculate_wage_stats,
                # "Company Funds": self.get_company_funds,
                # "Total Funds": lambda m: round(sum(self.get_company_funds()), 2),
                # "Product Fill Rates": lambda m: round(self.get_companies_product_fill_rate(), 2),
                # "Iterative Profits": self.calculate_profits,
                "Company Profit Average": self.calculate_average_profits
            }
        )
        self.model = model

    def calculate_average_tenure(self) -> float:
        ended_work_records = [wr for e in self.model.employees for wr in e.work_records if wr.to_time is not None]
        if len(ended_work_records) == 0:
            return 0
        lenghts = calculate_work_lengths(ended_work_records)
        return sum(lenghts) / len(lenghts)

    def calculate_average_profits(self) -> float:
        return sum((c.funds - c.starting_funds) / c.starting_funds for c in self.model.companies) / len(self.model.companies)

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
        return {c.unique_id: c.funds for c in self.model.companies}

    def calculate_profits(self) -> list[dict[int, float]]:
        if len(self.company_funds) < 2:
            return [0] * len(self.model.companies)
        latest_funds = self.company_funds[-1]
        before_latest_funds = self.company_funds[-2]

        profits = {}
        for user_id in latest_funds:
            if user_id in before_latest_funds:
                profits[user_id] = (latest_funds[user_id] - before_latest_funds[user_id]) / before_latest_funds[user_id]

        return profits

    def get_companies_product_fill_rate(self) -> float:
        return sum([c._calculate_total_productivity() / c.available_sellable_products_count for c in self.model.companies]) / len(self.model.companies)

def calculate_work_lengths(all_ended_work_records: list[WorkRecord]) -> list[int]:
    return [r.to_time - r.from_time for r in all_ended_work_records]
