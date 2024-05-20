import logging
import solara

from matplotlib.figure import Figure
import mesa
from mesa.visualization.UserParam import UserParam

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

    grid = mesa.visualization.CanvasGrid(agent_portrayal, 19, 19, 500, 500)
    unemployment_chart = mesa.visualization.ChartModule(
        [{"Label": "Unemployment Rate", "Color": "Black"}],
        data_collector_name="datacollector", canvas_height=200, canvas_width=500
    )
    time_spent_chart = mesa.visualization.ChartModule(
        [{"Label": "Average Work Tenure", "Color": "Blue"}],
        data_collector_name="datacollector"
    )
    # company_funds_chart = mesa.visualization.ChartModule(
    #     [{"Label": "Company Funds", "Color": "Red"}],
    #     data_collector_name="datacollector"
    # )
    company_funds_chart = mesa.visualization.ChartModule(
        [{"Label": f"Company #{i} Funds", "Color": f"#{i*123456 % 0xFFFFFF:06X}"} for i in range(9)],
        data_collector_name='datacollector'
    )

    # company_param = UserParam("slider", "Company count", 9, 1, 10, 1)
    employee_slider = mesa.visualization.Slider("Employee count", 95, 1, 100)
    company_slider = mesa.visualization.Slider("Company count", 9, 1, 10)
    quitting_slider = mesa.visualization.Slider("Quitting multiplier", 1, 0, 5, 0.1)
    product_cost_slider = mesa.visualization.Slider("Product cost", 222, 1, 1000, 10)
    initial_employment_slider = mesa.visualization.Slider("Initial employment rate", 0.94, 0, 1, 0.01)

    params = {
        "num_employees": employee_slider,
        "num_companies": company_slider,
        "settings": settings,
        "initial_employment_rate": initial_employment_slider,
        "quitting_multiplier": quitting_slider,
        "product_cost": product_cost_slider,
    }

    server = mesa.visualization.ModularServer(
        LaborModel, [grid, unemployment_chart, time_spent_chart, company_funds_chart], "Labor Market Model", params)

    server.port = 8521  # The default
    server.launch()


if __name__ == "__main__":
    main()
