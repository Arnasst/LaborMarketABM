from random import random

import mesa
from openai import OpenAI

from labor_model.company_agent_base import CompanyAgentBase
from labor_model.employee_agent import Application
from labor_model.llm_deciding import Decision, ask_about_employee_count
from labor_model.local_logging import logger


class CompanyLLMAgent(CompanyAgentBase):
    open_ai: OpenAI
    step_decision: Decision

    def __init__(
        self,
        unique_id: int,
        model: mesa.Model,
        market_share: float,
        productivity_ratio: float,
        available_sellable_products_count: int,
        funds: int,
        open_ai: OpenAI,
    ):
        super().__init__(
            unique_id,
            model,
            market_share,
            productivity_ratio,
            available_sellable_products_count,
            funds,
        )

        self.open_ai = open_ai
        self.step_decision = Decision.NOTHING

    def step(self):
        logger.info(f"Company #{self.unique_id} step. Funds: {self.funds:.2f}. ")

        total_productivity = self._calculate_total_productivity()
        monthly_employee_cost = sum(
            employee.current_salary for employee in self.employees
        )
        monthly_earnings = self._calculate_earnings()
        logger.info(
            f"Company #{self.unique_id} monthly earnings: {monthly_earnings:.2f}. Monthly employee cost: {monthly_employee_cost:.2f}."
        )

        self.funds -= monthly_employee_cost
        self.funds += monthly_earnings
        selling_all = total_productivity >= self.available_sellable_products_count

        employment_decision = ask_about_employee_count(self.open_ai, self.funds, selling_all)
        logger.debug(f"Company #{self.unique_id}: Employment decision: {employment_decision}")
        self.step_decision = employment_decision

        if employment_decision == Decision.HIRE:
            if self.applications:
                best_application = self._choose_best_application()
                self._hire_applicant(best_application)
            self.accepting_applications = True
        elif employment_decision == Decision.FIRE:
            worst_employee = self._choose_who_to_fire()
            self._fire_employee(worst_employee)
            self.accepting_applications = False

        self.applications = []


    def _choose_best_application(self) -> Application:
        logger.debug(f"Company #{self.unique_id}: Choosing best application")

    def _choose_who_to_fire(self) -> bool:
        logger.debug(f"Company #{self.unique_id}: Choosing who to fire")
