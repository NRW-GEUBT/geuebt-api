from __future__ import annotations

import datetime
from enum import Enum
from typing import Optional, Dict, List
from typing_extensions import Annotated

from beanie import Document
from pydantic import BaseModel, Field


# Special Types Definitions ===============================


class _OrganismEnum(str, Enum):
    """
    Define accepted organisms
    """
    listeria = 'Listeria monocytogenes'
    salmonella = 'Salmonella enterica'
    ecoli = 'Escherichia coli'
    campy = 'Campylobacter spp.'


# Nested Fields Models ====================================


class _Subcluster(BaseModel):
    subcluster_id: str
    subcluster_number: Annotated[int, Field(ge=0)]
    size: Annotated[int, Field(ge=0)]
    representative: str
    AD_threshold: Annotated[int, Field(ge=0)]
    members: List[str]


class _PublicAnnotation(BaseModel):
    user: str
    date: Optional[datetime.datetime] | None = datetime.datetime.now()
    message: str


class _Priority(BaseModel):
    level: int
    date: Optional[datetime.datetime] | None = datetime.datetime.now()
    user: str
    history: Optional[_Priority] | None = None


class _TagInfo(BaseModel):
    tag_id: str
    tag_origin: str
    date: Optional[datetime.datetime] | None = datetime.datetime.now()


# Document Model ==========================================


class ClusterSheet(Document):
    """Cluster sheet document specifications"""
    cluster_id: str
    created_at: Optional[datetime.datetime] | None = datetime.datetime.now()
    updated_at: Optional[datetime.datetime] | None = datetime.datetime.now()
    cluster_number: Annotated[int, Field(ge=0)]
    organism: _OrganismEnum
    priority: _Priority
    tags: Optional[List[_TagInfo]] | None = None
    public_annotation: Optional[List[_PublicAnnotation]] | None = None
    size: Annotated[int, Field(ge=0)]
    representative: Optional[str] | None = None
    AD_threshold: Annotated[int, Field(ge=0)]
    root_members: Optional[List[str]] | None = None
    subclusters: Optional[List[_Subcluster]] | None = None
    distance_matrix: List[Dict[str, int]]
    tree: str
    
    class Settings:
        name = "clusters"
        keep_nulls = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "cluster_id": "RRW_SA-34",
                "cluster_number": 34,
                "organism": "Salmonella enterica",
                "priority": {"level": 3, "user": "system"},
                "size": 3,
                "representative": "2024-5300721",
                "AD_threshold": 10,
                "root_members": None,
                "subclusters": [
                    {
                        "subcluster_id": "SA-34.1",
                        "subcluster_number": 1,
                        "size": 3,
                        "representative": "2024-5300721",
                        "AD_threshold": 5,
                        "members": [
                            "2024-5300721",
                            "2024-5300722",
                            "2024-8600579"
                        ]
                    }
                ],
                "distance_matrix": [
                    {
                        "2024-5300721": 0,
                        "2024-5300722": 1,
                        "2024-8600579": 0
                    },
                    {
                        "2024-5300721": 1,
                        "2024-5300722": 0,
                        "2024-8600579": 1
                    },
                    {
                        "2024-5300721": 0,
                        "2024-5300722": 1,
                        "2024-8600579": 0
                    }
                ],
                "tree": "(2024-5300722:1,2024-8600579:0,2024-5300721:0);\n"
            }
        }


# Query Models ============================================


class OnlyID(BaseModel):
    cluster_id: str

    class Settings:
        projection = {"cluster_id": 1}
