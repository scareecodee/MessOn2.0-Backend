from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    database_hostname: str
    database_port: int
    database_username: str
    database_password: str
    database_name: str
    access_token_secret: str
    refresh_token_secret: str
    algorithm: str
    access_token_expire_days: int
    refresh_token_expire_days: int
    google_client_id:str
    breakfast_expire:str
    lunch_expire:str
    dinner_expire:str
    coupon_secret_key:str
    max_notifications:int
    max_csv_file_size:int
    csv_upload_timelimit:int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()





