from random import random

import mesa

from labor_model.employee_agent import Application, EmployeeAgent
from labor_model.local_logging import logger
from labor_model.utils import COST_PER_HIRE


class CompanyAgentBase(mesa.Agent):
    funds: int
    market_share: float
    available_sellable_products_count: int

    accepting_applications: bool
    applications: list[Application]
    employees: list[EmployeeAgent]

    def __init__(
        self,
        unique_id: int,
        model: mesa.Model,
        market_share: float,
        productivity_ratio: float,
        available_sellable_products_count: int,
        funds: int,
    ):
        super().__init__(unique_id, model)

        self.productivity_ratio = productivity_ratio
        self.market_share = market_share
        self.available_sellable_products_count = available_sellable_products_count

        self.accepting_applications = True
        self.applications = []
        self.employees = []

        self.funds = funds

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

        if self._contemplate_hiring(total_productivity):
            additional_productivity = 0
            if self.applications:
                best_application = self._choose_best_application()
                self._hire_applicant(best_application)
                additional_productivity = best_application.employee.productivity
            if self._contemplate_hiring(total_productivity + additional_productivity):
                self.accepting_applications = True
        else:
            self.accepting_applications = False

        self.applications = []

        if self.employees and self._decide_whether_to_fire(
            monthly_employee_cost, monthly_earnings, total_productivity
        ):
            self._fire_inefficient_employee()

    def _calculate_earnings(self) -> float:
        return self._calculate_total_productivity() * self.model.product_cost

    def _calculate_total_productivity(self) -> float:
        return self.productivity_ratio * sum(
            employee.productivity for employee in self.employees
        )

    def _fire_inefficient_employee(self):
        least_efficient_employee = max(
            self.employees,
            key=lambda employee: employee.current_salary / employee.productivity,
        )
        self._fire_employee(least_efficient_employee)

    def _fire_employee(self, employee):
        self.employees.remove(employee)
        logger.info(
            f"Company #{self.unique_id} fired employee #{employee.unique_id}"
        )
        employee.change_work_state()

    def _hire_applicant(self, application: Application):
        applicant = application.employee
        if not applicant.is_working:
            logger.warning(
                f"Company #{self.unique_id} hired employee #{applicant.unique_id}"
            )
            self.employees.append(applicant)
            applicant.change_work_state(self.unique_id, application.desired_salary)

            self.funds -= COST_PER_HIRE
        else:
            logger.info(
                f"Company #{self.unique_id} unable to hire employee #{applicant.unique_id}, because he is already working"
            )
        self.applications.remove(application)

    def _refuse_applicant(self, application: Application):
        applicant = application.employee
        logger.info(
            f"Company #{self.unique_id} refused employee #{applicant.unique_id}"
        )
        self.applications.remove(application)

    def _choose_best_application(self) -> Application:
        raise NotImplementedError

    def _decide_whether_to_fire(
        self,
        monthly_employee_cost: int,
        monthly_earnings: float,
        total_productivity: float,
    ) -> bool:
        raise NotImplementedError

    def _contemplate_hiring(self, total_productivity: float) -> bool:
        raise NotImplementedError
