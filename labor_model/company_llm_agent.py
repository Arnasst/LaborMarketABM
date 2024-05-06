import mesa
from openai import OpenAI

from labor_model.company_agent_base import CompanyAgentBase
from labor_model.employee_agent import Application, EmployeeAgent
from labor_model.llm_deciding import Decision, ask_about_employee_count, ask_which_to_fire, ask_which_to_hire
from labor_model.local_logging import logger


class CompanyLLMAgent(CompanyAgentBase):
    open_ai: OpenAI
    previous_decision: Decision

    def __init__(
        self,
        unique_id: int,
        model: mesa.Model,
        market_share: float,
        available_sellable_products_count: int,
        funds: int,
        open_ai: OpenAI,
    ):
        super().__init__(
            unique_id,
            model,
            market_share,
            available_sellable_products_count,
            funds,
        )

        self.open_ai = open_ai
        self.previous_decision = Decision.NOTHING

    def step(self):
        logger.info(f"Company #{self.unique_id} step. Funds: {self.funds:.2f}. Decision: {self.previous_decision}.")

        total_productivity = self._calculate_total_productivity()
        monthly_operating_cost = self._calculate_monthly_expenses()
        monthly_earnings = self._calculate_earnings()
        logger.info(
            f"Company #{self.unique_id} monthly earnings: {monthly_earnings:.2f}. Monthly employee cost: {monthly_operating_cost:.2f}."
        )

        self.funds -= monthly_operating_cost
        self.funds += monthly_earnings
        logger.debug(f"Company #{self.unique_id}: Total productivity: {total_productivity:.2f}. Available sellable products: {self.available_sellable_products_count}.")
        selling_all = total_productivity < self.available_sellable_products_count

        if self.previous_decision != Decision.HIRE:
            employment_decision = ask_about_employee_count(self.open_ai, self.funds, selling_all, monthly_earnings, monthly_operating_cost)
        else:
            employment_decision = Decision.HIRE
        logger.debug(f"Company #{self.unique_id}: Employment decision: {employment_decision}")
        self.previous_decision = employment_decision

        if employment_decision == Decision.HIRE:
            self.accepting_applications = True
            if self.applications:
                best_application = self._choose_best_application()
                if self._hire_applicant(best_application):
                    self.accepting_applications = False
                    self.previous_decision = Decision.NOTHING
        elif employment_decision == Decision.FIRE:
            worst_employee = self._choose_who_to_fire()
            self._fire_employee(worst_employee)
            self.accepting_applications = False

        self.applications = []


    def _choose_best_application(self) -> Application:
        logger.debug(f"Company #{self.unique_id}: Choosing best application")
        return ask_which_to_hire(self.open_ai, self.funds, self.applications)

    def _choose_who_to_fire(self) -> EmployeeAgent:
        logger.debug(f"Company #{self.unique_id}: Choosing who to fire")
        return ask_which_to_fire(self.open_ai, self.employees)
