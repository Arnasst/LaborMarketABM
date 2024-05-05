from random import random

import mesa
import numpy as np
from openai import OpenAI

from labor_model.company_agent import CompanyAgent
from labor_model.config import Settings
from labor_model.employee_agent import EmployeeAgent, Seniority
from labor_model.local_logging import logger
from labor_model.step_stats_collector import StepStatsCollector
from labor_model.utils import (AVERAGE_PRODUCTIVITY, INFLATION_RATE,
                               JOBS_TO_EMPLOYEES_RATIO)


class LaborModel(mesa.Model):
    agent_id_iter: int

    product_cost: float
    company_operating_cost: int
    cost_per_hire: int

    employees: list[EmployeeAgent]
    companies: list[CompanyAgent]
    bankrupt_companies: list[CompanyAgent]

    quit_count: int
    fire_count: int

    def __init__(
        self,
        num_employees: int,
        num_companies: int,
        settings: Settings,
        llm_based: bool = False,
        open_ai_client: OpenAI | None = None,
    ):
        # Worksim model

        # µ0 Average base hourly production for blue collar jobs 4.92
        # µ1 Average base hourly production for middle level jobs 5.53
        # µ2 Average base hourly production for manager jobs 6.88

        # µΨ0 Average demand share allocated to blue collar jobs 33.5%
        # µΨ1 Average demand share allocated to middle level jobs 28.1%
        # µΨ2 Average demand share allocated to manager jobs 38.4%

        # Required level of seniority for a promotion (in weeks) 556

        # Average monthly salary - blue collar/employee 15-24 yr (euros) 1336 1158
        # Average monthly salary - blue collar/employee 25-49 yr (euros) 1624 1416
        # Average monthly salary - blue collar/employee 50-64 yr (euros) 1724 1904
        # Average monthly salary - middle level job 15-24 yr (euros) 1603 1200
        # Average monthly salary - middle level job 25-49 yr (euros) 2143 1835
        # Average monthly salary - middle level job 50-64 yr (euros) 2496 2822
        # Average monthly salary - manager 15-24 yr (euros) 2079 1363
        # Average monthly salary - manager 25-49 yr (euros) 3558 2935
        # Average monthly salary - manager 50-64 yr (euros) 4485 4782

        # Share of the base productivity value kept by the firm 0.71

        # https://www.payscale.com/content/report/2024-compensation-best-practice-report.pdf
        # 3% is the average base pay increase predicted for 2024
        # 6% more jobs than employees

        # https://uk.indeed.com/career-advice/pay-salary/salary-increase-changing-jobs-uk
        # Changing jobs results in around 10% salary increase
        super().__init__()

        self.product_cost = settings.initial_product_cost
        self.company_operating_cost = settings.base_operating_cost
        self.cost_per_hire = settings.cost_per_hire
        self.initial_salary = settings.initial_salary
        self.changing_jobs_raise = settings.changing_jobs_raise
        self.quitting_multiplier = settings.quitting_multiplier

        self.total_products = (
            num_employees * AVERAGE_PRODUCTIVITY * JOBS_TO_EMPLOYEES_RATIO
        )

        self.num_companies = num_companies
        self.num_employees = num_employees
        # Gal random activation? Nes dabar kai kurie advantaged yra
        self.schedule = mesa.time.SimultaneousActivation(self)
        self.companies = []
        self.bankrupt_companies = []
        self.employees = []

        self.quit_count = 0
        self.fire_count = 0

        initial_market_shares = self.get_initial_market_shares()
        for i in range(self.num_companies):
            company_available_products = int(
                self.total_products * initial_market_shares[i]
            )
            company_funds = company_available_products * self.product_cost * 3

            c = CompanyAgent(
                i,
                self,
                initial_market_shares[i],
                company_available_products,
                company_funds,
            )
            self.companies.append(c)
            self.schedule.add(c)

        current_companies_idx = 0
        for i in range(self.num_companies, self.num_employees + self.num_companies):
            employee_productivity = self._generate_employee_productivity_ratio()
            e = EmployeeAgent(i, self, Seniority.JUNIOR, employee_productivity)
            self.employees.append(e)
            self.schedule.add(e)

            if current_companies_idx < len(self.companies):
                current_company = self.companies[current_companies_idx]
                current_company_productivity = (
                    current_company._calculate_total_productivity()
                )
                if (
                    current_company_productivity
                    < settings.initial_employment_rate
                    * current_company.available_sellable_products_count
                    / JOBS_TO_EMPLOYEES_RATIO
                ):
                    current_company.employees.append(e)
                    e.change_work_state(current_company.unique_id, self.initial_salary)
                else:
                    current_companies_idx += 1

        self.agent_id_iter = self.num_employees + self.num_companies

        self.datacollector = StepStatsCollector(self)

    def step(self):
        self.datacollector.collect(self)

        logger.debug(f"Model step {self.schedule.steps}")
        if self.schedule.steps % 12 == 0:
            logger.info("Adjusting market shares")
            self._adjust_market_shares()
            self.product_cost *= 1 + INFLATION_RATE
            self._apply_company_yearly_raises()

        self.schedule.step()

        if bankrupt_company := next(
            (
                company
                for company in self.companies
                if company.funds < 2000 and len(company.employees) == 0
            ),
            None,
        ):
            logger.warning(f"Company #{bankrupt_company.unique_id} went bankrupt")
            logger.warning(f"Company #{self.agent_id_iter} takes over the market share")
            self.bankrupt_companies.append(bankrupt_company)
            self.companies.remove(bankrupt_company)

            company_available_products = int(
                self.total_products * bankrupt_company.market_share
            )
            new_company_funds = company_available_products * self.product_cost * 3
            new_company = CompanyAgent(
                self.agent_id_iter,
                self,
                bankrupt_company.market_share,
                company_available_products,
                new_company_funds,
            )
            self.companies.append(new_company)
            self.agent_id_iter += 1

    # [AVERAGE_PRODUCTIVITY - 1, AVERAGE_PRODUCTIVITY + 1]
    def _generate_employee_productivity_ratio(self) -> float:
        return AVERAGE_PRODUCTIVITY - 1 + random() * 2

    def get_initial_market_shares(self) -> np.ndarray:
        numbers = np.random.rand(self.num_companies)
        normalized_numbers = numbers / np.sum(numbers)

        min_share_for_6_products = 6 / self.total_products

        adjusted_numbers = np.maximum(normalized_numbers, min_share_for_6_products)
        adjusted_shares = adjusted_numbers / np.sum(adjusted_numbers)

        return adjusted_shares

    def _adjust_market_shares(self) -> None:
        # Mean (trend) for the stochastic shock
        µ = random() / 10
        # Volatility factor for the stochastic shock
        o = random() / 10

        for company in self.companies:
            company.market_share = max(
                0, company.market_share * (1 + np.random.normal(µ, o))
            )
            company.available_sellable_products_count = int(
                company.market_share * self.total_products
            )

        # Adjust market shares to ensure the sum equals 1
        total_market_share = sum(company.market_share for company in self.companies)
        for company in self.companies:
            company.market_share /= total_market_share

    def _apply_company_yearly_raises(self) -> None:
        for company in self.companies:
            if company.funds > 5000:
                for employee in company.employees:
                    employee.current_salary *= 1 + INFLATION_RATE
