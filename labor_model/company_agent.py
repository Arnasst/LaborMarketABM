from random import random

from labor_model.company_agent_base import CompanyAgentBase
from labor_model.employee_agent import Application
from labor_model.utils import AVERAGE_PRODUCTIVITY


class CompanyAgent(CompanyAgentBase):
    def _choose_best_application(self) -> Application:
        return min(
            self.applications,
            key=lambda application: application.desired_salary
            / (application.employee.productivity - 1 + random() * 2),
        )

    def _decide_whether_to_fire(
        self,
        monthly_employee_cost: int,
        monthly_earnings: float,
        total_productivity: float,
    ) -> bool:
        if self.funds < self._calculate_monthly_expenses() * self.model.company_emergency_months:
            return True
        if (
            monthly_employee_cost > monthly_earnings
            or total_productivity > self.available_sellable_products_count
        ):
            return random() < self.model.company_fire_probability
        return False

    def _contemplate_hiring(self, total_productivity: float) -> bool:
        average_salary = self._calculate_employee_average_salary()
        if (
            self.funds > self.model.cost_per_hire + 2 * average_salary
            and total_productivity
            < self.available_sellable_products_count - AVERAGE_PRODUCTIVITY
        ):
            return True
        return False

    def _calculate_employee_average_salary(self) -> float:
        if not self.employees:
            return self.model.initial_salary
        return sum(employee.current_salary for employee in self.employees) / len(
            self.employees
        )
