import logging

import mesa

from labor_model.company_agent_base import CompanyAgentBase
from labor_model.config import Settings
from labor_model.employee_agent import EmployeeAgent
from labor_model.local_logging import logger
from labor_model.model import LaborModel


def agent_portrayal(agent):
    portrayal = {"Shape": "circle", "Filled": "true", "r": 0.5}

    company_agents = [agent for agent in agent.model.schedule.agents if isinstance(agent, CompanyAgentBase)]
    max_funds = max([company_agent.funds for company_agent in company_agents])

    if isinstance(agent, CompanyAgentBase):
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 0
        portrayal["r"] = agent.funds / max_funds
    else:
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2

    return portrayal

def main():
    logger.setLevel(logging.WARNING)
    settings = Settings()

    NUM_EMPLOYEES = 10
    NUM_COMPANIES = 5

    grid = mesa.visualization.CanvasGrid(agent_portrayal, 10, 10, 500, 500)
    chart = mesa.visualization.ChartModule(
        [{"Label": "Gini", "Color": "Black"}], data_collector_name="datacollector"
    )

    server = mesa.visualization.ModularServer(
        LaborModel, [grid, chart], "Labor Market Model", {"num_employees": NUM_EMPLOYEES, "num_companies": NUM_COMPANIES, "settings": settings}
    )
    server.port = 8521  # The default
    server.launch()


if __name__ == "__main__":
    main()
