from __future__ import annotations
from pathlib import Path
import json
from typing import Any, Dict, List, Optional
import duckdb

class DESSRepository:
    def __init__(self, duckdb_path: Path, curated_dir: Path):
        self.duckdb_path = Path(duckdb_path)
        self.curated_dir = Path(curated_dir)

    def _connect(self):
        return duckdb.connect(str(self.duckdb_path), read_only=True)

    def json_file(self, *parts: str) -> Dict[str, Any]:
        path = self.curated_dir.joinpath(*parts)
        with path.open('r', encoding='utf-8') as f:
            return json.load(f)

    def table_count(self, table: str) -> int:
        with self._connect() as con:
            return int(con.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0])

    def rows(self, table: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        limit = max(1, min(int(limit), 1000))
        offset = max(0, int(offset))
        with self._connect() as con:
            return con.execute(f'SELECT * FROM {table} LIMIT ? OFFSET ?', [limit, offset]).fetchdf().to_dict('records')

    def predictions(self, limit: int = 40, system_id: Optional[int] = None) -> List[Dict[str, Any]]:
        path = self.curated_dir / 'dess_target_predictions.parquet'
        with self._connect() as con:
            if system_id is None:
                return con.execute('SELECT * FROM read_parquet(?) ORDER BY system_id, k_index LIMIT ?', [str(path), int(limit)]).fetchdf().to_dict('records')
            return con.execute('SELECT * FROM read_parquet(?) WHERE system_id = ? ORDER BY k_index LIMIT ?', [str(path), int(system_id), int(limit)]).fetchdf().to_dict('records')

    def metrics(self) -> Dict[str, Any]:
        return self.json_file('model', 'metrics.json')

    def stats(self) -> Dict[str, Any]:
        return self.json_file('physics_stats.json')

    def qc(self) -> Dict[str, Any]:
        return self.json_file('qc_report.json')

    def artifact_manifest(self) -> Dict[str, Any]:
        return self.json_file('model', 'artifact_manifest.json')

    def score_by_smiles(self, table: str, smiles: str) -> Optional[Dict[str, Any]]:
        with self._connect() as con:
            df = con.execute(f'SELECT * FROM {table} WHERE smiles = ? OR canonical_smiles = ? LIMIT 1', [smiles, smiles]).fetchdf()
        if df.empty:
            return None
        return df.iloc[0].to_dict()

    def average_product_score(self) -> Dict[str, float]:
        with self._connect() as con:
            df = con.execute('SELECT AVG(p_physics) p_physics, AVG(stability_support) stability_support, AVG(uncertainty) uncertainty FROM product_physics_scores').fetchdf()
        row = df.iloc[0].to_dict()
        return {k: float(row[k] or 0.0) for k in row}
