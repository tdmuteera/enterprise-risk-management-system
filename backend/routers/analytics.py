"""Analytics API router."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from models.risk import User
from schemas.analytics import (
    HeatmapResponse,
    InstitutionalSummaryResponse,
    RiskChainGraphResponse,
    TrendPoint,
)
from services.analytics_service import heatmap, institutional_summary, risk_chain_graph, trend
from utils.db_dep import get_db

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/trend", response_model=list[TrendPoint])
async def trend_endpoint(
    dept_id: Optional[UUID] = None,
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await trend(db, dept_id=dept_id, days=days)


@router.get("/heatmap", response_model=HeatmapResponse)
async def heatmap_endpoint(
    dept_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HeatmapResponse:
    cells = await heatmap(db, dept_id=dept_id)
    return HeatmapResponse(dept_id=dept_id, cells=cells)


@router.get("/institutional-summary", response_model=InstitutionalSummaryResponse)
async def institutional_summary_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InstitutionalSummaryResponse:
    data = await institutional_summary(db)
    return InstitutionalSummaryResponse(departments=data["departments"], distribution=data["distribution"])


@router.get("/risk-chain-graph", response_model=RiskChainGraphResponse)
async def risk_chain_graph_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RiskChainGraphResponse:
    data = await risk_chain_graph(db)
    return RiskChainGraphResponse(nodes=data["nodes"], edges=data["edges"])
