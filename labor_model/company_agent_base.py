from random import random

import mesa

from labor_model.employee_agent import Application, EmployeeAgent
from labor_model.local_logging import logger


class CompanyAgentBase(mesa.Agent):
    starting_funds: float
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
        available_sellable_products_count: int,
        funds: int,
    ):
        super().__init__(unique_id, model)

        self.market_share = market_share
        self.available_sellable_products_count = available_sellable_products_count

        self.accepting_applications = True
        self.applications = []
        self.employees = []

        self.starting_funds = funds
        self.funds = funds

    def step(self):
        logger.info(f"Company #{self.unique_id} step. Funds: {self.funds:.2f}. ")

        total_productivity = self._calculate_total_productivity()
        monthly_expenses = self._calculate_monthly_expenses()
        monthly_earnings = self._calculate_earnings()
        logger.info(
            f"Company #{self.unique_id} monthly earnings: {monthly_earnings:.2f}. Monthly expenses: {monthly_expenses:.2f}."
        )

        self.funds -= monthly_expenses
        self.funds += monthly_earnings

        if self._contemplate_hiring(total_productivity):
            additional_productivity = 0
            if self.applications:
                for _ in range(3):
                    best_application = self._choose_best_application()
                    if self._hire_applicant(best_application):
                        break
                additional_productivity = best_application.employee.productivity
            if self._contemplate_hiring(total_productivity + additional_productivity):
                self.accepting_applications = True
        else:
            self.accepting_applications = False

        self.applications = []

        if self.employees and self._decide_whether_to_fire(
            monthly_expenses, monthly_earnings, total_productivity
        ):
            self._fire_inefficient_employee()

    def _calculate_monthly_expenses(self) -> float:
        return sum(
            employee.current_salary for employee in self.employees
        ) + self.model.company_operating_cost

    def _calculate_earnings(self) -> float:
        return self._calculate_total_productivity() * self.model.product_cost

    def _calculate_total_productivity(self) -> float:
        return sum(
            employee.productivity for employee in self.employees
        )

    def _fire_inefficient_employee(self):
        least_efficient_employee = max(
            self.employees,
            key=lambda employee: employee.current_salary / employee.productivity,
        )
        self._fire_employee(least_efficient_employee)

    def _fire_employee(self, employee: EmployeeAgent):
        self.model.fire_count += 1
        self.employees.remove(employee)
        logger.info(
            f"Company #{self.unique_id} fired employee #{employee.unique_id}"
        )
        employee.change_work_state()

    def _hire_applicant(self, application: Application) -> bool:
        applicant = application.employee
        self.applications.remove(application)
        if not applicant.is_working:
            logger.warning(
                f"Company #{self.unique_id} hired employee #{applicant.unique_id}"
            )
            self.employees.append(applicant)
            applicant.change_work_state(self.unique_id, application.desired_salary)

            self.funds -= self.model.cost_per_hire
        else:
            logger.info(
                f"Company #{self.unique_id} unable to hire employee #{applicant.unique_id}, because he is already working"
            )
            return False
        return True

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
