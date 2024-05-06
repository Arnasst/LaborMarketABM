from enum import Enum
from openai import OpenAI
from labor_model.employee_agent import Application, EmployeeAgent


HR_CHOOSE_PROMPT = "You are an HR assistant. Your answer to each question should be only the number of the chosen person."
HR_HIRE_FIRE_PROMPT = "You are an HR assistant. Hiring costs 2000. Your answers to each question should be Hire, Fire or Nothing." # Firing saves money, but reduces income.
SELLING_ALL_PROMPT = "We are selling all products that we produce"
PRODUCING_TOO_MUCH_PROMPT = "We are producing more than we can sell"

FUNDS_PROMPT_F = lambda funds: f"We currently have {funds}$"

HIRE_FIRE_QUESTION_PROMPT = "Should we hire more people, do nothing or fire someone?"

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
    return Decision(response_content)

def ask_which_to_hire(client: OpenAI, applicants: list[Application]) -> bool:
    pass

def ask_which_to_fire(client: OpenAI, employees: list[EmployeeAgent]) -> bool:
    pass
