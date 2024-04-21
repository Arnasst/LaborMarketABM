from random import random

import mesa
from openai import OpenAI

from labor_model.company_agent_base import CompanyAgentBase
from labor_model.utils import AVERAGE_PRODUCTIVITY, COST_PER_HIRE


class CompanyLLMAgent(CompanyAgentBase):
    open_ai: OpenAI

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

    def _decide_whether_to_fire(
        self,
        monthly_employee_cost: int,
        monthly_earnings: float,
        total_productivity: float,
    ) -> bool:
        if self.funds < 1500:
            return True
        if (
            monthly_employee_cost > monthly_earnings
            or total_productivity > self.available_sellable_products_count
        ):
            return random() < 0.2
        return False

    def _contemplate_hiring(self, total_productivity: float) -> bool:
        if (
            self.funds > COST_PER_HIRE
            and total_productivity
            < self.available_sellable_products_count - AVERAGE_PRODUCTIVITY
        ):
            return True
        return False
