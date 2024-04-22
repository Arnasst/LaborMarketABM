from enum import StrEnum
from openai import OpenAI
from labor_model.employee_agent import Application, EmployeeAgent


HR_PROMPT = "You are an HR assistant. Your answers to each question should be Yes or No"
HR_HIRE_FIRE_PROMPT = "You are an HR assistant. Your answers to each question should be Hire or Fire"
SELLING_ALL_PROMPT = "We are selling all products that we produce"
PRODUCING_TOO_MUCH_PROMPT = "We are producing more than we can sell"

FUNDS_PROMPT_F = lambda funds: f"We currently have {funds}$"

HIRE_FIRE_QUESTION_PROMPT = "Should we hire more people or fire someone?"

class Decision(StrEnum):
    HIRE = "Hire"
    FIRE = "Fire"

def ask_about_hiring(client: OpenAI, funds: int, selling_all: bool) -> bool:
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
