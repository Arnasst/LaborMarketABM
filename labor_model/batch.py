import logging
from mesa.batchrunner import batch_run

from labor_model.config import Settings
from labor_model.model import LaborModel

def main() -> None:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)

    settings = Settings()

    NUM_EMPLOYEES = 150

    parameters = {
        "num_employees": NUM_EMPLOYEES,
        "num_companies": range(10, 15),
        "settings": [settings for _ in range(1)],
        "llm_based": False,
        "open_ai_client": None
    }

    results = batch_run(
        model_cls=LaborModel,
        parameters=parameters,
        number_processes=None,
        iterations=1,
        max_steps=12,
        display_progress=True
    )

if __name__ == "__main__":
    main()
