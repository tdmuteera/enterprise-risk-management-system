"""Pydantic schemas for Analytics API."""

from datetime import date
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TrendPoint(BaseModel):
    day: date
    avg_score: float = 0.0
    risk_count: int = 0


class HeatmapCell(BaseModel):
    likelihood: int
    impact: int
    count: int


class HeatmapResponse(BaseModel):
    dept_id: Optional[UUID] = None
    cells: List[HeatmapCell] = Field(default_factory=list)


class InstitutionalDepartmentSummary(BaseModel):
    department_id: UUID
    department_name: str
    iri: float = 0.0
    total_risks: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


class InstitutionalSummaryResponse(BaseModel):
    departments: List[InstitutionalDepartmentSummary] = Field(default_factory=list)
    distribution: Dict[str, int] = Field(default_factory=dict)


class GraphNode(BaseModel):
    id: str
    title: str
    department_id: str
    normalised_score: float


class GraphEdge(BaseModel):
    source: str
    target: str
    weight: float
    link_type: str


class RiskChainGraphResponse(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
