import datetime
from enum import Enum
from typing import Optional

from beanie import Document


# Special Types Definitions ===============================


class _FileTypesEnum(str, Enum):
    fasta = "fasta"


# Document Model ==========================================


class Sequence(Document):
    """Sequence file"""
    isolate_id: str
    created_at: Optional[datetime.datetime] | None = datetime.datetime.now()
    updated_at: Optional[datetime.datetime] | None = None
    sequence_type: _FileTypesEnum
    sequence: str
    
    class Settings:
        name = "sequences"
        keep_nulls = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "isolate_id": "2024-12345678-01",
                "sequence_type": "fasta",
                "sequence": ">contig0001 len=35\nATCTGTCCGTAGCTGACGTGCAAGAGCTCGATCGA\n"
            }
        }
