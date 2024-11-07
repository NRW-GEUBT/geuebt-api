from typing import List

from fastapi import APIRouter, HTTPException
from beanie.operators import Set

from server.models.clusters import ClusterSheet, OnlyID


router = APIRouter()


@router.put("/{cluster_id}", response_description="Create or Update cluster record")
async def upsert_cluster(cluster_id: str, cluster: ClusterSheet) -> dict:
    # Likely almost all fields change on every update so upsert whole document
    # For update, ignore created_at field
    await ClusterSheet.find_one(
        ClusterSheet.cluster_id == cluster_id
    ).upsert(
        Set(
            {
                ClusterSheet.updated_at: cluster.updated_at,
                ClusterSheet.size: cluster.size,
                ClusterSheet.root_members: cluster.root_members,
                ClusterSheet.subclusters: cluster.subclusters,
                ClusterSheet.distance_matrix: cluster.distance_matrix,
                ClusterSheet.tree: cluster.tree,
            }
        ), 
        on_insert = cluster
    )
    return {"message": "Cluster added succesfully"}


@router.get("/", response_description="List clusters in collection")
async def get_cluster_ids(species = None) -> List[OnlyID]:
    if species:
        docs = await ClusterSheet.find(
            ClusterSheet.organism == species,
            ClusterSheet.cluster_number > 0
        ).project(
            OnlyID
        ).to_list()
    else:
        docs = await ClusterSheet.find(
            ClusterSheet.cluster_number > 0
        ).project(
            OnlyID
        ).to_list()
    return docs


@router.get("/{cluster_id}", response_description="Get cluster by ID")
async def get_cluster(cluster_id: str) -> ClusterSheet:
    doc = await ClusterSheet.find(
        ClusterSheet.cluster_id == cluster_id
    ).first_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")
    return doc


@router.get("/{species}/orphans", response_description="Get orphan cluster for species")
async def get_orphans(species: str) -> ClusterSheet:
    doc = await ClusterSheet.find(
        ClusterSheet.organism == species,
        ClusterSheet.cluster_number == 0
    ).first_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")
    return doc