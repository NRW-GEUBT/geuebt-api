from fastapi import FastAPI

from server.database import init_db
from server.routes.isolates import router as IsolatesRouter
from server.routes.sequences import router as SequencesRouter
from server.routes.clusters import router as ClustersRouter
from server.routes.runs import router as RunRouter


app= FastAPI()
app.include_router(IsolatesRouter, tags=["Isolate sheets"], prefix="/isolates")
app.include_router(SequencesRouter, tags=["Sequence files"], prefix="/sequences")
app.include_router(ClustersRouter, tags=["Cluster sheets"], prefix="/clusters")
app.include_router(RunRouter, tags=["Run reports"], prefix="/runs")



@app.on_event("startup")
async def start_db():
    await init_db()


@app.get("/")
async def read_root() -> dict:
    return {"message": "Nothing to do here"}
