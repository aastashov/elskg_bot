from dataclasses import dataclass
from pathlib import Path

import environ


@dataclass
class Settings:
    def __post_init__(self):
        self.PROJECT_ROOT = Path(__file__).parent.resolve().parent

        env = environ.Env()
        environ.Env.read_env(f"{self.PROJECT_ROOT}/.env")

        self.TG_API_TOKEN = env.str("TG_API_TOKEN", default="")


settings = Settings()
