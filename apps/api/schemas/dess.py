from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ArtifactHealth(BaseModel):
    ok: bool
    model_version: str
    artifact_version: str
    schema_version: str
    rows: Dict[str, int]
    qc_ok: bool
    target_columns: List[str]
    best_epoch: Optional[int] = None
    test_raw_mse: Optional[float] = None
    database_path: str

class MetricResponse(BaseModel):
    model_version: str
    best_score: Optional[float]
    best_epoch: Optional[int]
    test_loss: Optional[float]
    test_raw_mse: Optional[float]
    test_rmse_per_target: Dict[str, float]
    history_preview: List[Dict[str, Any]]

class PredictionRow(BaseModel):
    system_id: int
    geom_id: int
    k_index: int
    y_true: Dict[str, float]
    y_pred: Dict[str, float]
    uncertainty: Optional[float] = None
    p_physics: Optional[float] = None
    stability_support: Optional[float] = None
    rank_score: Optional[float] = None

class PredictionList(BaseModel):
    rows: List[PredictionRow]
    count: int

class ScoreRow(BaseModel):
    id: str
    smiles: str
    canonical_smiles: str
    p_physics: float
    stability_support: float
    uncertainty: float
    score_source: str

class CandidateRank(BaseModel):
    candidate_id: str
    reactant_set_id: str
    rank_score: float
    physics_support: float
    stability_support: float
    uncertainty: float

class LabScoreRequest(BaseModel):
    reactants: List[str] = Field(default_factory=list)
    candidates: List[str] = Field(default_factory=list)

class LabScoreResponse(BaseModel):
    reactant_scores: List[ScoreRow]
    candidate_scores: List[ScoreRow]
    rank_scores: List[CandidateRank]
    note: str

class ArtifactSummary(BaseModel):
    stats: Dict[str, Any]
    qc: Dict[str, Any]
    policies: Dict[str, Any]
    artifact_manifest: Dict[str, Any]


class ExplainRequest(BaseModel):
    reactant_scores: List[ScoreRow] = Field(default_factory=list)
    candidate_scores: List[ScoreRow] = Field(default_factory=list)
    rank_scores: List[CandidateRank] = Field(default_factory=list)
    note: Optional[str] = None
    user_context: Optional[str] = None

class ExplainResponse(BaseModel):
    ai_mode: str
    summary: str
    interpretation: List[str]
    recommended_next_steps: List[str]
    caveats: List[str]
    markdown: str
