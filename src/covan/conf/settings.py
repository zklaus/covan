from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "covan"
    debug: bool = False
