from __future__ import annotations

from pathlib import Path
from typing import Iterable

from core.config import Settings


DESS_ASSET_FILES = (
    'dess_physics/curated/v1/candidate_rank_scores.parquet',
    'dess_physics/curated/v1/dess_target_predictions.parquet',
    'dess_physics/curated/v1/inputs/candidate_inputs.parquet',
    'dess_physics/curated/v1/inputs/inputs_manifest.json',
    'dess_physics/curated/v1/inputs/reactant_inputs.parquet',
    'dess_physics/curated/v1/model/artifact_manifest.json',
    'dess_physics/curated/v1/model/audit.json',
    'dess_physics/curated/v1/model/config.normalized.json',
    'dess_physics/curated/v1/model/dess66x8_v2.pt',
    'dess_physics/curated/v1/model/dess66x8_v2_best.pt',
    'dess_physics/curated/v1/model/dess66x8_v2_metrics.json',
    'dess_physics/curated/v1/model/dess66x8_v2_test_preds.csv',
    'dess_physics/curated/v1/model/dess66x8_v2_trial001_audit.json',
    'dess_physics/curated/v1/model/metrics.json',
    'dess_physics/curated/v1/physics_stats.json',
    'dess_physics/curated/v1/product_physics_scores.parquet',
    'dess_physics/curated/v1/qc_report.json',
    'dess_physics/curated/v1/raw_dess_predictions.parquet',
    'dess_physics/curated/v1/reactant_physics_scores.parquet',
    'dess_physics/staging/dess_physics.duckdb',
)


def _missing_files(root: Path, files: Iterable[str]) -> list[str]:
    return [filename for filename in files if not (root / filename).exists()]


def ensure_dess_assets(settings: Settings) -> None:
    """Ensure the DESS artifact bundle exists locally, hydrating from Hugging Face if needed."""

    cache_dir = settings.dess_asset_cache_dir
    missing = _missing_files(cache_dir, DESS_ASSET_FILES)
    if not missing:
        return

    if not settings.hf_download_enabled:
        missing_preview = ', '.join(missing[:5])
        raise RuntimeError(
            f'DESS assets are missing under {cache_dir}. Missing examples: {missing_preview}. '
            'Enable HF_DOWNLOAD_ENABLED or provide the local artifact bundle.'
        )

    try:
        from huggingface_hub import hf_hub_download
    except ImportError as exc:
        raise RuntimeError('huggingface-hub is required to download DESS assets at runtime.') from exc

    cache_dir.mkdir(parents=True, exist_ok=True)
    for filename in missing:
        hf_hub_download(
            repo_id=settings.dess_asset_repo_id,
            repo_type=settings.dess_asset_repo_type,
            filename=filename,
            local_dir=cache_dir,
            local_dir_use_symlinks=False,
        )

    still_missing = _missing_files(cache_dir, DESS_ASSET_FILES)
    if still_missing:
        raise RuntimeError(f'DESS assets could not be resolved: {", ".join(still_missing)}')
