from typing import List

from fastapi import APIRouter, HTTPException

from server.models.runs import RunReport, OnlyID


router = APIRouter()


@router.post("/", response_description="Create run record")
async def create_run(report: RunReport) -> dict:
    if await RunReport.find(RunReport.run_metadata.name == report.run_metadata.name).first_or_none():
        body = [{
            "type": "str",
            "loc": [
                "body",
                "isolate_id"
            ],
            "msg": "A document with this ID already exists in the collection",
            "input": report.run_metadata.name,
            "ctx": {
                "expected": ""
            }
        }]
        raise HTTPException(status_code=422, detail=body)
    await report.create()
    return {"message": "Report added succesfully"}


@router.get("/", response_description="List runs in collection")
async def get_run_ids(species = None) -> List[OnlyID]:
    docs = await RunReport.find_all().project(OnlyID).to_list()
    return docs


@router.get("/{run_name}", response_description="Read run record")
async def get_run(run_name: str) -> RunReport:
    doc = await RunReport.find(RunReport.run_metadata.name == run_name).first_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")
    return doc
