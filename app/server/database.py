import os

from beanie import init_beanie
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


async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(
        os.environ.get('MONGO_URL')
    )
    await init_beanie(
        database=client[os.environ.get('MONGO_DB')],
        document_models=doc_models)
