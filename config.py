from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from pydantic_settings import BaseSettings
from supabase import Client, create_client

from src.repo.assessments_repo import AssessmentsDataRepository
from src.repo.repo import UserDataRepository


class Secrets(BaseSettings):
    token: str
    url: str
    key: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

secrets = Secrets()

url: str = secrets.url
key: str = secrets.key

supabase: Client = create_client(url, key)

users_data_repo = UserDataRepository(supabase)
assessments_data_repo = AssessmentsDataRepository(supabase)

default = DefaultBotProperties(parse_mode='Markdown', protect_content=True)
bot = Bot(token = secrets.token, default=default)
dp = Dispatcher()




