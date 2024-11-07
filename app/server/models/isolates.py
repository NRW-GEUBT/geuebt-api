import datetime
from enum import Enum
from typing import Optional, List
from typing_extensions import Annotated

from beanie import Document
from pydantic_core import PydanticCustomError
from pydantic import (
    BaseModel,
    PastDate,
    Field,
    model_validator,
)


# Special Types Definitions ===============================


class _OrganismEnum(str, Enum):
    """
    Define accepted organisms
    """
    listeria = 'Listeria monocytogenes'
    salmonella = 'Salmonella enterica'
    ecoli = 'Escherichia coli'
    campy = 'Campylobacter spp.'


class _UserEnum(str, Enum):
    """
    Define accepted users
    Ideally should come from Database, for future versions
    """
    owl = 'OWL'
    rrw = 'RRW'
    mel = 'MEL'
    wfl = 'WFL'
    rld = 'RLD'
    other = 'other'


class _SampleTypesEnum(str, Enum):
    """
    Define accepted sample types
    """
    food = "Lebensmittel"
    feed = "Futtermittel"
    env = "Umfeld"
    vet = "Tiergesundheit"
    human = "Human"
    ringtrial = "Ringtrial"
    other = "unknown"


# Nested Fields Models ====================================


class _SampleInfo(BaseModel):
    """Part of IsolateSheet - sample processing info"""
    isolation_org: _UserEnum
    isolation_org: _UserEnum
    sequencing_org: _UserEnum
    bioinformatics_org: _UserEnum   
    extraction_method: Optional[str] | None = None
    library_kit: Optional[str] | None = None
    sequencing_kit: Optional[str] | None = None
    sequencing_instrument: Optional[str] | None = None
    assembly_method: Optional[str] | None = None


class _Epidata(BaseModel):
    """Part of IsolateSheet - epidemiological metadata"""
    collection_date: Optional[PastDate] | None = datetime.date(1970, 1, 1)
    customer: Optional[str] | None = "NNNNN"
    manufacturer: Optional[str] | None = "unknown"
    collection_place: Optional[str] | None = "unknown"
    description: Optional[str] | None = "unknown"
    manufacturer_type: Optional[str] | None = None
    manufacturer_type_code: Optional[str] | None = None
    matrix: Optional[str] | None = None
    matrix_code: Optional[str] | None = None
    collection_cause: Optional[str] | None = None
    collection_cause_code: Optional[str] | None = None
    lot_number: Optional[str] | None = None


class _QCmetrics(BaseModel):
    """Part of IsolateSheet - Sampe QC"""
    seq_depth: Annotated[float, Field(ge=0)]
    ref_coverage: Annotated[float, Field(ge=0, le=1)]
    q30: Annotated[float, Field(ge=0.75, le=1)]
    N50: Annotated[int, Field(ge=0)]
    L50: Annotated[int, Field(ge=0)]
    n_contigs_1kbp: Annotated[int, Field(ge=0)]
    assembly_size: Annotated[int, Field(ge=0)]
    GC_perc: Annotated[float, Field(ge=0, le=100)]
    orthologs_found: Annotated[float, Field(ge=0, le=100)]
    duplicated_orthologs: Annotated[float, Field(ge=0, le=100)]
    majority_genus: str
    fraction_majority_genus: Annotated[float, Field(ge=0, le=1)]
    majority_species: str
    fraction_majority_species: Annotated[float, Field(ge=0, le=1)]
    cgmlst_missing_fraction: Optional[Annotated[float, Field(ge=0, le=1)]] | None = None


class _QCmissingloci(BaseModel):
    """Add fraction missing loci to QC metrics - Part of AddAlleleProfile"""
    cgmlst_missing_fraction: Annotated[float, Field(ge=0, le=1)]


class _LocusInfo(BaseModel):
    locus: str
    allele_crc32: int


class _AlleleStats(BaseModel):
    """Chewbbacca stats"""
    EXC: Annotated[int, Field(ge=0)]
    INF: Annotated[int, Field(ge=0)]
    LNF: Annotated[int, Field(ge=0)]
    PLOT: Annotated[int, Field(ge=0)]
    NIPH: Annotated[int, Field(ge=0)]
    ALM: Annotated[int, Field(ge=0)]
    ASM: Annotated[int, Field(ge=0)]


class _CGMLSTInfo(BaseModel):
    allele_profile: List[_LocusInfo]
    allele_stats: _AlleleStats


# Document Model ==========================================


class IsolateSheet(Document):
    """Metadata format V3 (ongoing) for internal validation"""
    isolate_id: str
    created_at: Optional[datetime.datetime] | None = datetime.datetime.now()
    updated_at: Optional[datetime.datetime] | None = None
    sample_id: str
    alt_isolate_id: Optional[str] | None = None
    organism: _OrganismEnum
    third_party_owner: Optional[str] | None = None
    sample_type: _SampleTypesEnum
    fasta_name: str
    fasta_md5: str
    sample_info: _SampleInfo
    epidata: _Epidata
    qc_metrics: _QCmetrics
    cgmlst: Optional[_CGMLSTInfo] | None = None
    
    @model_validator(mode='after')
    def check_coverage(self):
        depth = self.qc_metrics.seq_depth
        organism = self.organism
        min_coverages = {
            'Listeria monocytogenes': 20,
            'Salmonella enterica': 30,
            'Escherichia coli': 40,
            'Campylobacter spp.': 20,
        }
        if depth < min_coverages[organism] or depth > 200:
            raise PydanticCustomError(
                "value_error",
                f"Value error: 'coverage' for '{organism}' must be between "
                f"'{min_coverages[organism]}' and 200, got {depth}.",
            )
        return self

    @model_validator(mode='after')
    def check_species_specific_assembly_size(self):
        expect = self.organism
        assembly = self.qc_metrics.assembly_size
        qcdict = {
            'Listeria monocytogenes': [2700000, 3200000],
            'Salmonella enterica': [4300000, 5200000],
            'Escherichia coli': [4500000, 5900000],
            'Campylobacter spp.': [1500000, 1900000],
        }
        if assembly < qcdict[expect][0] or assembly > qcdict[expect][1]:
            raise PydanticCustomError(
                "value_error",
                f"Value error: 'assembly_size' for '{expect}' must be between "
                f"{qcdict[expect][0]} and {qcdict[expect][1]}, got: {assembly}",
            )
        return self

    @model_validator(mode='after')
    def check_species_specific_orthologs_found(self):
        expect = self.organism
        ortho = self.qc_metrics.orthologs_found
        qcdict = {
            'Listeria monocytogenes': 95,
            'Salmonella enterica': 95,
            'Escherichia coli': 95,
            'Campylobacter spp.': 80,
        }
        if ortho < qcdict[expect]:
            raise PydanticCustomError(
                "value_error",
                f"Value error: 'orthologs_found' for '{expect}' must be at least {qcdict[expect]}, got: {ortho}",
            )
        return self

    @model_validator(mode='after')
    def check_species_specific_duplicated_orthologs(self):
        expect = self.organism
        dup = self.qc_metrics.duplicated_orthologs
        qcdict = {
            'Listeria monocytogenes': 5,
            'Salmonella enterica': 5,
            'Escherichia coli': 5,
            'Campylobacter spp.': 5,
        }
        if dup > qcdict[expect]:
            raise PydanticCustomError(
                "value_error",
                f"Value error: 'duplicated_orthologs' for '{expect}' must be at most {qcdict[expect]}, got: {dup}",
            )
        return self

    @model_validator(mode='after')
    def check_species_specific_fraction_majority_genus(self):
        expect = self.organism
        frac = self.qc_metrics.fraction_majority_genus
        qcdict = {
            'Listeria monocytogenes': 0.9,
            'Salmonella enterica': 0.9,
            'Escherichia coli': 0.9,
            'Campylobacter spp.': 0.9,
        }
        if frac < qcdict[expect]:
            raise PydanticCustomError(
                "value_error",
                f"Value error: 'fraction_majority_genus' for '{expect}' must be at least {qcdict[expect]}, got: {frac}",
            )
        return self

    @model_validator(mode='after')
    def check_species_specific_majority_genus(self):
        expect = self.organism
        genus = self.qc_metrics.majority_genus
        qcdict = {
            'Listeria monocytogenes': ["Listeria"],
            'Salmonella enterica': ["Salmonella"],
            'Escherichia coli': ["Escherichia", "Shigella"],
            'Campylobacter spp.': ["Campylobacter"],
        }
        if genus not in qcdict[expect]:
            raise PydanticCustomError(
                "value_error",
                f"Value error: 'majority_genus' for '{expect}' must be in {qcdict[expect]}, got: {genus}",
            )
        return self

    class Settings:
        name = "isolates"
        keep_nulls = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "isolate_id": "2024-12345678-01",
                "sample_id": "2024-12345678",
                "alt_isolate_id": "24LIS123456-01",
                "organism": "Listeria monocytogenes",
                "third_party_owner": None,
                "sample_type": "Lebensmittel",
                "fasta_name": "2024-12345678-01.fa",
                "fasta_md5": "0dd766ecb53be1a4d9459bab262ea712",
                "sample_info": {
                    "isolation_org": "RRW",
                    "isolation_org": "RRW",
                    "sequencing_org": "RRW",
                    "bioinformatics_org": "RRW",
                    "extraction_method": "Qiagen - QiAmp",
                    "library_kit": "DNA Illumina Prep",
                    "sequencing_kit": "MiSeq v2 (300 cycles)",
                    "sequencing_instrument": "MiSeq",
                    "assembly_method": "AQUAMIS v2.3.5"
                },
                "epidata": {
                    "collection_date": "2024-10-08",
                    "customer": "DU",
                    "manufacturer": "WurstFabrik",
                    "collection_place": "Metzger Rainer",
                    "description": "Wurst, rund und lang",
                    "manufacturer_type": "Wurstler",
                    "manufacturer_type_code": "12365|12365|",
                    "matrix": "Wurst",
                    "matrix_code": "|74125|12369|",
                    "collection_cause": "Planprobe",
                    "collection_cause_code": "85213|25469|",
                    "lot_number": "2365478"
                },
                "qc_metrics": {
                    "seq_depth": 45.6,
                    "ref_coverage": 0.99,
                    "q30": 0.98,
                    "N50": 510409,
                    "L50": 3,
                    "n_contigs_1kbp": 13,
                    "assembly_size": 2881087,
                    "GC_perc": 37.92,
                    "orthologs_found": 100,
                    "duplicated_orthologs": 0.8,
                    "majority_genus": 'Listeria',
                    "fraction_majority_genus": 0.99,
                    "majority_species": 'Listeria monocytogenes',
                    "fraction_majority_species": 0.99,
                }
            }
        }


# Update Models ===========================================


class AddAlleleProfile(BaseModel):
    updated_at: Optional[datetime.datetime] | None = datetime.datetime.now()
    qc_metrics: _QCmissingloci
    cgmlst: _CGMLSTInfo

    class Config:
        json_schema_extra = {
            "example": {
                "qc_metrics": {
                    "cgmlst_missing_fraction": 0.002
                },
                "cgmlst": {
                    "allele_profile": [
                        {
                            "locus": "lmo0001.fasta",
                            "allele_crc32": 3453202319
                        },
                        {
                            "locus": "lmo0002.fasta",
                            "allele_crc32": 138852938
                        },
                        {
                            "locus": "lmo0003.fasta",
                            "allele_crc32": 2562060452
                        }
                    ],
                    "allele_stats": {
                        "EXC": 3,
                        "INF": 0,
                        "LNF": 1,
                        "PLOT": 0,
                        "NIPH": 2,
                        "ALM": 3,
                        "ASM": 0
                    }
                }
            }
        }


# Query Models ============================================


class OnlyID(BaseModel):
    isolate_id: str

    class Settings:
        projection = {"isolate_id": 1}


class QueryProfiles(BaseModel):
    isolate_id: str
    profile: List[_LocusInfo]

    class Settings:
        projection = {"isolate_id": 1, "profile": "$cgmlst.allele_profile"}
