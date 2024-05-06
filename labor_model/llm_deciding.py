from enum import Enum
from openai import OpenAI
from labor_model.employee_agent import Application, EmployeeAgent
from labor_model.local_logging import logger


HR_HIRE_FIRE_PROMPT = "You are an HR assistant. Hiring costs 2000. Your answers to each question should be 'Hire', 'Fire' or 'Nothing'."
SELLING_ALL_PROMPT = "We are selling all products that we produce"
PRODUCING_TOO_MUCH_PROMPT = "We are producing more than we can sell"
# Add prompt about how much earning, spending, etc.

FUNDS_PROMPT_F = lambda funds: f"We currently have {int(funds)}$"

HIRE_FIRE_QUESTION_PROMPT = "Should we hire more people, do nothing or fire someone?"

HR_CHOOSE_PROMPT = "You are an HR assistant. Your answer to each question should be only the number of the chosen person."
LIST_WORKER_PROMPT = "These people are working in our company. Who to let go? Here are their (productivity, salary)"
LIST_APPLICANTS_PROMPT = "These people are applying to our company. Who to hire? Here are their (productivity, desired salary)"

class Decision(Enum):
    HIRE = "Hire"
    FIRE = "Fire"
    NOTHING = "Nothing"

def ask_about_employee_count(client: OpenAI, funds: int, selling_all: bool) -> bool:
    selling_prompt = SELLING_ALL_PROMPT if selling_all else PRODUCING_TOO_MUCH_PROMPT
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": HR_HIRE_FIRE_PROMPT},
            {
                "role": "user",
                "content": f"{FUNDS_PROMPT_F(funds)}. {selling_prompt}. {HIRE_FIRE_QUESTION_PROMPT}",
            },
        ],
    )
    response_content = response.choices[0].message.content
    logger.debug(f"Question: '{FUNDS_PROMPT_F(funds)}. {selling_prompt}. {HIRE_FIRE_QUESTION_PROMPT}'.\nAnswer: '{response_content}'")
    response_content = response_content.replace(".", "")
    return Decision(response_content)

def ask_which_to_hire(client: OpenAI, applicants: list[Application]) -> bool:
    application_list = "; ".join(f"#{a.employee.unique_id} ({round(a.employee.productivity, 1)}, {int(a.desired_salary)})" for a in applicants)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": HR_CHOOSE_PROMPT},
            {"role": "user", "content": f"{LIST_APPLICANTS_PROMPT}: {application_list}"},
        ],
    )
    response_content = response.choices[0].message.content
    logger.debug(f"Question: '{LIST_APPLICANTS_PROMPT}: {application_list}'.\nAnswer: '{response_content}'")
    employee_id = int(response_content[1:])
    application = next(a for a in applicants if a.employee.unique_id == employee_id)
    return application

def ask_which_to_fire(client: OpenAI, employees: list[EmployeeAgent]) -> EmployeeAgent:
    employees_list = "; ".join(f"#{e.unique_id} ({round(e.productivity, 1)}, {int(e.current_salary)})" for e in employees)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": HR_CHOOSE_PROMPT},
            {"role": "user", "content": f"{LIST_WORKER_PROMPT}: {employees_list}"},
        ],
    )
    response_content = response.choices[0].message.content
    logger.debug(f"Question: '{LIST_WORKER_PROMPT}: {employees_list}'.\nAnswer: '{response_content}'")
    employee_id = int(response_content[1:])
    employee = next(e for e in employees if e.unique_id == employee_id)
    return employee
