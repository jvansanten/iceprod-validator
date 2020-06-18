#!/usr/bin/env python3

from pydantic import BaseModel, Field, ValidationError, validator, root_validator
from typing import List, Dict, Any, Optional
from enum import Enum
import sys

class MachineRequirements(BaseModel):
    class Config:
        extra = 'forbid'
    memory: float = Field(1, description='Memory in GB')
    disk: float = Field(1, description="Local disk in GB")
    time: float = Field(1, description="Wallclock time in hours")
    os: Optional[str] = Field(None, description="OS_ARCH specification")
    cpu: int = Field(1, description="Number of CPU cores")
    gpu: int = Field(0, description="Number of GPUs")

class StorageType(str, Enum):
    permanent = "permanent"
    job_temp = "job_temp"

class MovementType(str, Enum):
    input = "input"
    output = "output"

class TransferType(str, Enum):
    exists = "exists"

class Data(BaseModel):
    class Config:
        extra = 'forbid'
    type: StorageType = Field(..., description='Type of storage. job_temp: temporary directory for each job')
    movement: MovementType = Field(..., description='When to move data files')
    transfer: TransferType = Field("exists", description='Conditions under which to move data files')
    remote: str = ""
    local: str = ""
    compression: bool = False

    @validator('remote', always=True)
    def check_remote(cls, field, values):
        if values.get('movement') == 'input':
            if values.get('type') == 'permanent':
                assert field, "remote must be set for input files from permanent storage"
        else:
            if values.get('type') == 'permanent':
                assert field, "remote must be set for output files to permanent storage"
        return field

class Class(BaseModel):
    class Config:
        extra = 'forbid'
    name: str
    src: str
    resource_name: str = ""
    recursive: bool = False
    libs: str = ""
    env_vars: str = ""

class Resource(BaseModel):
    class Config:
        extra = 'forbid'

class _Tasklike(BaseModel):
    name: str
    parameters: Dict[str,Any] = Field({}, description='Task-specific steering parameters')
    resources: List[Resource] = Field([], description='')
    data: List[Data] = Field([], description='Files required as input to or output from this task')
    classes: List[Class] = Field([], description='Software distributions, e.g. tarballs, required for this task')
    projects: List = Field([], description='A list of things that appears to always be empty')
    requirements: MachineRequirements = Field(MachineRequirements(), description='Minimum requirements to run this task')

class Module(_Tasklike):
    class Config:
        title = 'Module'
        description = 'A single process'
        extra = 'forbid'
    src: str = Field(..., description="Script to invoke")
    running_class: Optional[str] = Field(None, description="IPModule subclass to invoke")
    env_shell: str = Field(..., description="Script to initialize environment")
    env_clear: bool = Field(True, description="Run env_shell in an empty environment")
    args: Dict[str,Any] = Field(..., description="Module arguments")

class Tray(_Tasklike):
    class Config:
        title = 'Tray'
        description = 'A sequence of processes that can be invoked in multiple iterations'
        extra = 'forbid'
    iterations: int = Field(1, description="Number of reps to run")
    modules: List[Module] = Field(..., description="Scripts to invoke in this task")

class Task(_Tasklike):
    class Config:
        title = 'Task'
        description = 'An abstract task'
        extra = 'forbid'
    name: str = Field(..., description='Name of this abstract task')
    depends: List[str] = Field([], description='Names of tasks this task depends on')
    batchsys: Optional[str] = None
    trays: List[Tray]

class Dataset(BaseModel):
    class Config:
        extra = 'forbid'
    version: int
    dataset: Optional[int] = None
    parent_id: Optional[int] = None
    description: Optional[str] = None
    categories: List[str] = []
    difplus: Optional[Dict[str,Any]] = None
    options: Optional[Dict[str,Any]] = None
    steering: Optional[Dict[str,Any]] = {}
    tasks: List[Task]

if __name__ == "__main__":
    from argparse import ArgumentParser, FileType

    parser = ArgumentParser()
    parser.add_argument("config", type=FileType('r'))
    
    args = parser.parse_args()
    try:
        dc = Dataset.parse_raw(args.config.read())
    except ValidationError as exc:
        print(exc)
        sys.exit(1)
    # print(dc)
    # print(Dataset.schema_json(indent=2))