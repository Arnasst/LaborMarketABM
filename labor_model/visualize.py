import logging

import mesa

from labor_model.company_agent_base import CompanyAgentBase
from labor_model.config import Settings
from labor_model.employee_agent import EmployeeAgent
from labor_model.local_logging import logger
from labor_model.model import LaborModel


def agent_portrayal(agent):
    portrayal = {"Shape": "circle", "Filled": "true", "r": 0.5}

    if isinstance(agent, CompanyAgentBase):
        company_agents = [agent for agent in agent.model.schedule.agents if isinstance(agent, CompanyAgentBase)]
        max_funds = max(company_agent.funds for company_agent in company_agents)

        portrayal["Color"] = "blue"
        portrayal["Layer"] = 0
        portrayal["r"] = agent.funds / max_funds
    else:
        employee_agents = [agent for agent in agent.model.schedule.agents if isinstance(agent, EmployeeAgent)]
        max_salary = max(employee_agent.current_salary if employee_agent.current_salary else 0 for employee_agent in employee_agents)
        salary = agent.current_salary if agent.current_salary else 0

        if agent.is_working:
            portrayal["Color"] = "green"
            portrayal["r"] = 0.35 * salary / max_salary
        else:
            portrayal["Color"] = "red"
            portrayal["r"] = 0.2

        portrayal["Layer"] = 1
        # portrayal["x"] = x + 0.5 * (agent.unique_id % 10)  # Offset x by unique_id
        # portrayal["y"] = y + 0.5 * (agent.unique_id % 10)  # Offset y by unique_id

    return portrayal

def main():
    logger.setLevel(logging.WARNING)
    settings = Settings()

    NUM_EMPLOYEES = 95
    NUM_COMPANIES = 9

    grid = mesa.visualization.CanvasGrid(agent_portrayal, 19, 19, 700, 700)
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
