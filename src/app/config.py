from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = (
        "postgres+psycopg://postgres:postgres@localhost:5432/investigation"
    )
