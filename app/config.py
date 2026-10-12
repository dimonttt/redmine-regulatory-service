from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_db_host: str = "localhost"
    app_db_port: int = 5433
    app_db_name: str = "redmine_service"
    app_db_user: str = "app"
    app_db_password: str = "app"

    redmine_url: str = "http://localhost:3000"
    redmine_api_key: str = ""

    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str = "ollama"
    llm_model: str = "qwen2.5:7b"
    llm_max_suggestions: int = 3
    llm_max_hours_per_suggestion: int = 8

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.app_db_user}:{self.app_db_password}"
            f"@{self.app_db_host}:{self.app_db_port}/{self.app_db_name}"
        )

    class Config:
        env_file = ".env"


settings = Settings()