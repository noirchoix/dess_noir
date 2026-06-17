from __future__ import annotations
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    dess_asset_repo_id: str = 'noirchoix/dess-bridge-physics-lab'
    dess_asset_repo_type: str = 'dataset'
    dess_asset_cache_dir: Path = Path('./data')
    hf_download_enabled: bool = True
    dess_duckdb_path: Path = Path('./data/dess_physics/staging/dess_physics.duckdb')
    dess_curated_dir: Path = Path('./data/dess_physics/curated/v1')
    frontend_origin: str = 'http://localhost:5173'
    dess_max_limit: int = 500
    llm_provider: str = 'offline'
    deepseek_api_key: str = ''
    deepseek_model: str = 'deepseek-chat'
    gemini_api_key: str = ''
    gemini_model: str = 'gemini-2.5-flash'

settings = Settings()
