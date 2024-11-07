from fastapi import APIRouter, HTTPException

from server.models.sequences import Sequence


router = APIRouter()


@router.get("/{isolate_id}", response_description="Sequence record")
async def get_sequence(isolate_id: str) -> Sequence:
    doc = await Sequence.find(Sequence.isolate_id == isolate_id).first_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")
    return doc


@router.post("/", response_description="Create sequence record")
async def create_sequence(sequence: Sequence) -> dict:
    if await (Sequence.find(Sequence.isolate_id == sequence.isolate_id)).first_or_none():
        body = [{
            "type": "str",
            "loc": [
                "body",
                "isolate_id"
            ],
            "msg": "A document with this ID already exists in the collection",
            "input": sequence.isolate_id,
            "ctx": {
                "expected": ""
            }
        }]
        raise HTTPException(status_code=422, detail=body)
    await sequence.create()
    return {"message": "Sequence added succesfully"}

