from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone

def utc_now():
    return datetime.now(timezone.utc)

class ProjectStatus(str, Enum):
    PLANNING = "PLANNING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Entity(BaseModel):
    id: str
    type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=utc_now)

class Organization(Entity):
    type: str = "Organization"
    name: str
    balance: float

class Employee(Entity):
    type: str = "Employee"
    name: str
    role: str
    skills: List[str]
    morale: float = Field(ge=0.0, le=1.0)
    energy_level: float = Field(ge=0.0, le=1.0)
    salary: float

class Project(Entity):
    type: str = "Project"
    name: str
    status: ProjectStatus
    budget: float
    progress: float = Field(ge=0.0, le=1.0)
    deadline: datetime
    complexity: float = Field(ge=0.0, le=1.0)

class Relation(BaseModel):
    source_id: str
    target_id: str
    relation_type: str
    properties: Dict[str, Any] = Field(default_factory=dict)
