from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    open_ai_key: str

    initial_product_cost: int = 222
    base_operating_cost: int = 79
    cost_per_hire: int = 1500
    initial_salary: int = 1000

    changing_jobs_raise: float = 1.15

    initial_employment_rate: float = 0.94

    quitting_multiplier: float = 0.25

    company_fire_probability: float = 0.05
    company_emergency_months: float = 1.5

    model_config = SettingsConfigDict(
        env_file=Path(Path(__file__).parent.parent, ".env"), env_file_encoding="utf-8"
    )
