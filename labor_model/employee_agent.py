from dataclasses import dataclass
from enum import StrEnum

import mesa
from scipy.stats import dweibull, gamma

from labor_model.local_logging import logger
from labor_model.utils import (
                               decide_based_on_probability)

search_probability_f = dweibull(0.4093106, 0.9999999, 0.2369317)
leave_probability_f = gamma(1.6878294628925388, -0.3202142090949511, 15.104677133022975)


@dataclass
class WorkRecord:
    employer_id: int
    salary: int
    from_time: int
    to_time: int | None


@dataclass
class Application:
    employee: "EmployeeAgent"
    desired_salary: int


class Seniority(StrEnum):
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"


class EmployeeAgent(mesa.Agent):
    is_working: bool
    current_salary: int | None
    employer_id: int | None
    work_records: list[WorkRecord]

    time_in_state: int

    seniority: Seniority
    productivity: float

    def __init__(
        self,
        unique_id: int,
        model: mesa.Model,
        seniority: Seniority,
        productivity: float,
    ):
        super().__init__(unique_id, model)

        self.work_records = []

        self.time_in_state = 0
        self.is_working = False
        self.employer_id = None

        self.seniority = seniority
        self.productivity = productivity
        self.current_salary = None

    def change_work_state(
        self, employer_id: int | None = None, salary: int | None = None
    ):
        self.is_working = not self.is_working
        self.time_in_state = 0
        self.employer_id = employer_id

        if employer_id is not None:
            self.work_records.append(
                WorkRecord(employer_id, salary, self.model.schedule.steps, None)
            )
        else:
            self.work_records[-1].to_time = self.model.schedule.steps
            self.work_records[-1].salary = self.current_salary
        self.current_salary = salary

    def step(self):
        logger.debug(f"Employee #{self.unique_id} step")
        if not self.is_working:
            self._contemplate_working()
            self.time_in_state += 1
        else:
            if self._contemplate_leaving():
                self.change_work_state()
            else:
                self.time_in_state += 1

    def _contemplate_working(self):
        search_probability = search_probability_f.cdf(self.time_in_state)
        logger.debug(
            f"Employee #{self.unique_id} search probability: {search_probability}"
        )
        if True: # decide_based_on_probability(search_probability):
            selected_company = self._select_company()
            if selected_company:
                self._apply_to_company(selected_company)

    def _select_company(self):
        hiring_companies = list(
            filter(lambda c: c.accepting_applications, self.model.companies)
        )
        if not hiring_companies:
            return None
        return self.random.choice(hiring_companies)

    def _apply_to_company(self, company):
        logger.debug(
            f"Employee #{self.unique_id} applied to company #{company.unique_id}"
        )

        desired_salary = self._calculate_desired_salary()
        company.applications.append(Application(self, desired_salary))

    def _contemplate_leaving(self) -> bool:
        # Divide by two because employee can leave or company can fire
        leave_probability = leave_probability_f.pdf(self.time_in_state) * self.model.quitting_multiplier
        logger.debug(
            f"Employee #{self.unique_id} leave probability: {leave_probability}"
        )
        if decide_based_on_probability(leave_probability):
            logger.warning(
                f"Employee #{self.unique_id} left company #{self.employer_id}"
            )
            # Company unique_id should be the same as their index, might be a YAGNI
            company = next(
                filter(lambda c: c.unique_id == self.employer_id, self.model.companies)
            )
            company.employees.remove(self)
            self.model.quit_count += 1
            return True
        return False

    def _calculate_desired_salary(self) -> int:
        if not self.work_records:
            return self.model.initial_salary
        previous_salary = self.work_records[-1].salary

        # every month he asks for 1% less
        return round(
            previous_salary * (self.model.changing_jobs_raise - 0.01 * self.time_in_state)
        )
