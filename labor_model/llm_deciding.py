from enum import Enum
from openai import OpenAI
from labor_model.employee_agent import Application, EmployeeAgent
from labor_model.local_logging import logger


HR_HIRE_FIRE_PROMPT = "You are an HR assistant. Hiring costs 1500. Your answers to each question should be 'Hire', 'Fire' or 'Nothing'."
SELLING_ALL_PROMPT = "We are selling all products that we produce"
PRODUCING_TOO_MUCH_PROMPT = "We are producing more than we can sell"

FUNDS_PROMPT_F = lambda funds: f"We currently have {int(funds)}$"
EARN_SPEND_PROMPT_F = lambda earnings, spending: f"We earned {int(earnings)}$ and spent {int(spending)}$"

HIRE_FIRE_QUESTION_PROMPT = "What should we do?" # "Should we hire more people, do nothing or fire someone?"

HR_CHOOSE_PROMPT = "You are an HR assistant. Your answer to each question should be only the number of the chosen person."
LIST_WORKER_PROMPT = "These people are working in our company. Who to let go? Here are their (productivity, salary)"
LIST_APPLICANTS_PROMPT = "These people are applying to our company. Who to hire? Here are their (productivity, desired salary)"

class Decision(Enum):
    HIRE = "Hire"
    FIRE = "Fire"
    NOTHING = "Nothing"

def ask_about_employee_count(client: OpenAI, funds: int, selling_all: bool, earned: int, spent: int) -> bool:
    selling_prompt = SELLING_ALL_PROMPT if selling_all else PRODUCING_TOO_MUCH_PROMPT
    user_prompt = f"{FUNDS_PROMPT_F(funds)}. {EARN_SPEND_PROMPT_F(earned, spent)}. {selling_prompt}. {HIRE_FIRE_QUESTION_PROMPT}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": HR_HIRE_FIRE_PROMPT},
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )
    response_content = response.choices[0].message.content
    logger.debug(f"Question: '{user_prompt}'.\nAnswer: '{response_content}'")
    response_content = response_content.replace(".", "")
    return Decision(response_content)

def ask_which_to_hire(client: OpenAI, funds: int, applicants: list[Application]) -> bool:
    application_list = "; ".join(f"#{a.employee.unique_id} ({round(a.employee.productivity, 1)}, {int(a.desired_salary)})" for a in applicants)
    user_prompt = f"{FUNDS_PROMPT_F(funds)}. {LIST_APPLICANTS_PROMPT}: {application_list}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": HR_CHOOSE_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    response_content = response.choices[0].message.content
    logger.debug(f"Question: '{user_prompt}'.\nAnswer: '{response_content}'")
    response_content = response_content.replace(".", "")

    try:
        employee_id_str = response_content[response_content.find("#")+1:]
        employee_id = [int(s) for s in employee_id_str.split() if s.isdigit()][0]
    except:
        logger.warning(f"Failed to parse application id from response: '{response_content}'")
        employee_id = [int(s) for s in response_content.split() if s.isdigit()][0]

    try:
        application = next(a for a in applicants if a.employee.unique_id == employee_id)
    except StopIteration:
        logger.warning(f"Failed to find application: '{response_content}'")
        application = applicants[(employee_id - 1) % len(applicants)]
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
    response_content = response_content.replace(".", "")

    try:
        employee_id_str = response_content[response_content.find("#")+1:]
        employee_id = [int(s) for s in employee_id_str.split() if s.isdigit()][0]
    except:
        logger.warning(f"Failed to parse employee id from response: '{response_content}'")
        employee_id = [int(s) for s in response_content.split() if s.isdigit()][0]

    try:
        employee = next(e for e in employees if e.unique_id == employee_id)
    except StopIteration:
        employee = employees[(employee_id - 1) % len(employees)]
    return employee
