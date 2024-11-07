from typing import List

from fastapi import APIRouter, HTTPException
from beanie.operators import Set

from server.models.isolates import IsolateSheet, AddAlleleProfile, QueryProfiles, OnlyID


router = APIRouter()


@router.post("/", response_description="Create isolate record with Metadata")
async def create_isolate(metadata: IsolateSheet) -> dict:
    if await IsolateSheet.find(IsolateSheet.isolate_id == metadata.isolate_id).first_or_none():
        body = [{
            "type": "str",
            "loc": [
                "body",
                "isolate_id"
            ],
            "msg": "A document with this ID already exists in the collection",
            "input": metadata.isolate_id,
            "ctx": {
                "expected": ""
            }
        }]
        raise HTTPException(status_code=422, detail=body)
    await metadata.create()
    return {"message": "Metadata added succesfully"}


@router.put("/{isolate_id}/allele_profile", response_description="Add allele profile to isolate record")
async def add_allele_profile(isolate_id: str, profile_info: AddAlleleProfile) -> dict:
    """Behaviour on existing profiles?"""
    # Check if doc exists
    doc = await IsolateSheet.find(IsolateSheet.isolate_id == isolate_id).first_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")
    # Update document
    await doc.update(Set(
        {
            "updated_at": profile_info.updated_at,
            "qc_metrics.cgmlst_missing_fraction": profile_info.qc_metrics.cgmlst_missing_fraction,
            "cgmlst": profile_info.cgmlst
        }
    ))
    return {"message": "Allele profile added succesfully"}


@router.get("/", response_description="List isolates in collection")
async def get_isolate_ids(species = None) -> list:
    if species:
        docs = await IsolateSheet.find(
            IsolateSheet.organism == species
        ).project(
            OnlyID
        ).to_list()
    else:
        docs = await IsolateSheet.find_all().project(OnlyID).to_list()
    return docs


@router.get("/{isolate_id}", response_description="Read isolate record")
async def get_isolate(isolate_id: str) -> IsolateSheet:
    doc = await IsolateSheet.find(IsolateSheet.isolate_id == isolate_id).first_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")
    return doc


@router.get("/{isolate_id}/allele_profile", response_description="Get allele profile for record")
async def get_profiles(isolate_id: str) -> QueryProfiles:
    doc = await IsolateSheet.find(
            IsolateSheet.isolate_id == isolate_id
        ).project(
            QueryProfiles
        ).first_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")
    return doc
