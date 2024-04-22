from random import random

import mesa
from openai import OpenAI

from labor_model.company_agent_base import CompanyAgentBase
from labor_model.employee_agent import Application


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

    def _choose_best_application(self) -> Application:
        pass

    def _decide_whether_to_fire(
        self,
        monthly_employee_cost: int,
        monthly_earnings: float,
        total_productivity: float,
    ) -> bool:
        pass

    def _contemplate_hiring(self, total_productivity: float) -> bool:
        pass
