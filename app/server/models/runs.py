import datetime
from enum import Enum
from typing import Optional, List

from beanie import Document
from pydantic import BaseModel


# Special Types Definitions ===============================


class _StatusFlag(str, Enum):
    passing = "PASS"
    failing = "FAIL"
    warning = "WARN"


# Nested Fields Models ====================================


class _RunMetadata(BaseModel):
    name: str
    date: Optional[datetime.datetime] | None = datetime.datetime.now()
    geuebt_version: str
    user: str


class _SampleQC(BaseModel):
    isolate_id: str
    STATUS: _StatusFlag
    MESSAGES: List[str]


# Document Model ==========================================


class RunReport(Document):
    """Analysis run report"""
    run_metadata: _RunMetadata
    samples: List[_SampleQC]

    class Settings:
        name = "runs"
        keep_nulls = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "run_metadata": {
                    "name": "test_run",
                    "geuebt_version": "1.0.0",
                    "user": "system"
                },
                "samples": [
                    {
                        "isolate_id": "2024-12345679-01 ",
                        "STATUS": "PASS",
                        "MESSAGES": [""]
                    },
                    {
                        "isolate_id": "2024-12345679-02 ",
                        "STATUS": "FAIL",
                        "MESSAGES": ["FAIL message", "Another message"] 
                    }
                ]
            }
        }


# Query models =========================================

class OnlyID(BaseModel):
    run_name: str

    class Settings:
        projection = {"run_name": "$run_metadata.name"}
