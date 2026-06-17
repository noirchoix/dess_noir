from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Query
from schemas.dess import ArtifactHealth, ArtifactSummary, ExplainRequest, ExplainResponse, LabScoreRequest, LabScoreResponse, MetricResponse, PredictionList
from services.dess_service import DESSService

router = APIRouter(prefix='/api/v1/dess', tags=['DESS physics'])
service = DESSService()

@router.get('/health', response_model=ArtifactHealth)
def health():
    return service.health()

@router.get('/summary', response_model=ArtifactSummary)
def summary():
    return service.summary()

@router.get('/metrics', response_model=MetricResponse)
def metrics():
    return service.metrics()

@router.get('/predictions', response_model=PredictionList)
def predictions(limit: int = Query(40, ge=1, le=500), system_id: Optional[int] = None):
    return service.predictions(limit=limit, system_id=system_id)

@router.get('/reactants')
def reactants(limit: int = Query(50, ge=1, le=500)):
    return service.reactants(limit=limit)

@router.get('/products')
def products(limit: int = Query(50, ge=1, le=500)):
    return service.products(limit=limit)

@router.get('/ranks')
def ranks(limit: int = Query(50, ge=1, le=500)):
    return service.ranks(limit=limit)

@router.post('/score', response_model=LabScoreResponse)
def score(payload: LabScoreRequest):
    return service.lab_score(payload.reactants, payload.candidates)

@router.post('/explain', response_model=ExplainResponse)
def explain(payload: ExplainRequest):
    return service.explain_score(payload.model_dump())
