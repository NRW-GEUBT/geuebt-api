from beanie import init_beanie
from pydantic_settings import BaseSettings, SettingsConfigDict
import motor.motor_asyncio

from server.models.isolates import IsolateSheet
from server.models.sequences import Sequence
from server.models.clusters import ClusterSheet
from server.models.runs import RunReport


doc_models = [
    IsolateSheet,
    Sequence,
    ClusterSheet,
    RunReport,
]


class Settings(BaseSettings):
    MONGO_URL: str
    MONGO_DB: str

    model_config = SettingsConfigDict(
        env_file='dotenv/fastapi.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )


settings = Settings()


async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.MONGO_URL
    )
    await init_beanie(
        database=client[settings.MONGO_DB],
        document_models=doc_models
    )
