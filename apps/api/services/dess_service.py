from __future__ import annotations

from typing import Any, Dict, List, Optional
import json

import requests

from core.config import settings
from repositories.dess_repository import DESSRepository
from services.hf_assets import ensure_dess_assets

TARGETS = [
    "cc_CCSD(T)_all",
    "sapt_es",
    "sapt_ind",
    "sapt_disp",
    "sapt_ex",
    "sapt_all",
]


class DESSService:
    def __init__(self):
        ensure_dess_assets(settings)
        self.repo = DESSRepository(settings.dess_duckdb_path, settings.dess_curated_dir)

    def health(self) -> Dict[str, Any]:
        stats = self.repo.stats()
        qc = self.repo.qc()
        metrics = self.repo.metrics()
        rows = dict(stats.get("rows") or {})

        for table in [
            "reactant_physics_scores",
            "product_physics_scores",
            "candidate_rank_scores",
        ]:
            try:
                rows[table] = self.repo.table_count(table)
            except Exception:
                pass

        cfg = self.repo.json_file("model", "config.normalized.json")

        return {
            "ok": bool(qc.get("ok")),
            "model_version": stats.get("model_version", "unknown"),
            "artifact_version": stats.get("artifact_version", "unknown"),
            "schema_version": stats.get("schema_version", "unknown"),
            "rows": rows,
            "qc_ok": bool(qc.get("ok")),
            "target_columns": list(cfg.get("target_cols") or TARGETS),
            "best_epoch": metrics.get("best_epoch"),
            "test_raw_mse": metrics.get("test_raw_mse"),
            "database_path": str(settings.dess_duckdb_path),
        }

    def summary(self) -> Dict[str, Any]:
        stats = self.repo.stats()
        return {
            "stats": stats,
            "qc": self.repo.qc(),
            "policies": stats.get("score_policies") or {},
            "artifact_manifest": self.repo.artifact_manifest(),
        }

    def metrics(self) -> Dict[str, Any]:
        m = self.repo.metrics()
        return {
            "model_version": self.health()["model_version"],
            "best_score": m.get("best_score"),
            "best_epoch": m.get("best_epoch"),
            "test_loss": m.get("test_loss"),
            "test_raw_mse": m.get("test_raw_mse"),
            "test_rmse_per_target": m.get("test_rmse_per_target") or {},
            "history_preview": (m.get("history") or [])[:12],
        }

    def _format_prediction(self, r: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "system_id": int(r["system_id"]),
            "geom_id": int(r["geom_id"]),
            "k_index": int(r["k_index"]),
            "y_true": {t: float(r.get("y_true_" + t, 0.0)) for t in TARGETS},
            "y_pred": {t: float(r.get("y_pred_" + t, 0.0)) for t in TARGETS},
            "uncertainty": None if r.get("uncertainty") is None else float(r.get("uncertainty")),
            "p_physics": None if r.get("p_physics") is None else float(r.get("p_physics")),
            "stability_support": None if r.get("stability_support") is None else float(r.get("stability_support")),
            "rank_score": None if r.get("rank_score") is None else float(r.get("rank_score")),
        }

    def predictions(self, limit: int = 40, system_id: Optional[int] = None) -> Dict[str, Any]:
        rows = [
            self._format_prediction(r)
            for r in self.repo.predictions(limit=limit, system_id=system_id)
        ]
        return {"rows": rows, "count": len(rows)}

    def reactants(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.repo.rows("reactant_physics_scores", limit=limit)

    def products(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.repo.rows("product_physics_scores", limit=limit)

    def ranks(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self.repo.rows("candidate_rank_scores", limit=limit)

    def _score_row(
        self,
        id_: str,
        smiles: str,
        source_table: str,
        prefix: str,
        idx: int,
    ) -> Dict[str, Any]:
        existing = self.repo.score_by_smiles(source_table, smiles)

        if existing:
            return {
                "id": str(existing.get("reactant_id") or existing.get("candidate_id") or id_),
                "smiles": smiles,
                "canonical_smiles": existing.get("canonical_smiles") or smiles,
                "p_physics": float(existing.get("p_physics") or 0),
                "stability_support": float(existing.get("stability_support") or 0),
                "uncertainty": float(existing.get("uncertainty") or 0),
                "score_source": "artifact_match",
            }

        avg = self.repo.average_product_score()
        modifier = min(0.08, (len(smiles) % 11) / 200)

        return {
            "id": f"{prefix}_{idx}",
            "smiles": smiles,
            "canonical_smiles": smiles,
            "p_physics": max(0.0, min(1.0, avg["p_physics"] - modifier)),
            "stability_support": max(0.0, min(1.0, avg["stability_support"] - modifier / 2)),
            "uncertainty": avg["uncertainty"] + modifier * 3,
            "score_source": "artifact_prior_no_live_inference",
        }

    def lab_score(self, reactants: List[str], candidates: List[str]) -> Dict[str, Any]:
        rs = [
            self._score_row(
                f"reactant_{i}",
                s,
                "reactant_physics_scores",
                "reactant",
                i,
            )
            for i, s in enumerate(reactants)
            if s.strip()
        ]

        cs = [
            self._score_row(
                f"candidate_{i}",
                s,
                "product_physics_scores",
                "candidate",
                i,
            )
            for i, s in enumerate(candidates)
            if s.strip()
        ]

        ranks = []
        for c in cs:
            physics = c["p_physics"]
            stability = c["stability_support"]
            unc = c["uncertainty"]
            rank = max(
                0.0,
                min(
                    1.0,
                    (0.6 * physics + 0.4 * stability) / (1.0 + 0.2 * unc),
                ),
            )
            ranks.append(
                {
                    "candidate_id": c["id"],
                    "reactant_set_id": "user_input_set",
                    "rank_score": rank,
                    "physics_support": physics,
                    "stability_support": stability,
                    "uncertainty": unc,
                }
            )

        return {
            "reactant_scores": rs,
            "candidate_scores": cs,
            "rank_scores": ranks,
            "note": (
                "Exact artifact matches use stored DESS bridge scores. "
                "New SMILES use a deterministic artifact-calibrated prior because live DESS graph inference "
                "is not bundled in this portfolio app."
            ),
        }

    def _llm_mode(self) -> str:
        provider = (settings.llm_provider or "offline").lower().strip()

        if provider == "deepseek" and settings.deepseek_api_key:
            return "deepseek"

        if provider == "gemini" and settings.gemini_api_key:
            return "gemini"

        return "offline"

    def explain_score(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explain a lab scoring result in plain language.

        The route is deliberately decoupled from scoring so the frontend can submit the
        exact run payload it already displayed. If no LLM key is configured, the method
        returns a deterministic explanation with the same schema.
        """
        mode = self._llm_mode()

        if mode != "offline":
            try:
                return self._llm_explain(payload, mode)
            except Exception as exc:
                fallback = self._offline_explain(payload)
                fallback["ai_mode"] = f"offline_fallback_after_{mode}_error"
                fallback["caveats"].append(
                    f"LLM explanation failed and offline interpretation was used: {exc}"
                )
                fallback["markdown"] = self._build_markdown(fallback)
                return fallback

        return self._offline_explain(payload)

    def _offline_explain(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        reactants = payload.get("reactant_scores") or []
        candidates = payload.get("candidate_scores") or []
        ranks = payload.get("rank_scores") or []
        top_rank = max(
            ranks,
            key=lambda r: float(r.get("rank_score") or 0),
            default=None,
        )

        def avg(rows: List[Dict[str, Any]], key: str) -> float:
            vals = [float(r.get(key) or 0) for r in rows]
            return sum(vals) / len(vals) if vals else 0.0

        avg_physics = avg(candidates or reactants, "p_physics")
        avg_stability = avg(candidates or reactants, "stability_support")
        avg_uncertainty = avg(candidates or reactants, "uncertainty")

        sources = sorted(
            {
                str(r.get("score_source") or "unknown")
                for r in [*reactants, *candidates]
            }
        )

        uncertainty_label = (
            "low"
            if avg_uncertainty < 1
            else "moderate"
            if avg_uncertainty < 3
            else "high"
        )
        support_label = (
            "strong"
            if avg_physics >= 0.7
            else "usable"
            if avg_physics >= 0.5
            else "weak"
        )
        stability_label = (
            "stable"
            if avg_stability >= 0.7
            else "moderately supported"
            if avg_stability >= 0.5
            else "low support"
        )

        summary = (
            f"This run shows {support_label} physics support and {stability_label} stability support, "
            f"with {uncertainty_label} uncertainty. The values should be read as ranking/support signals, "
            "not as direct reaction-yield predictions."
        )

        if top_rank:
            summary += (
                f" The top candidate in this run is {top_rank.get('candidate_id')} "
                f"with rank score {float(top_rank.get('rank_score') or 0):.3f}."
            )

        interpretation = [
            (
                f"Physics support averages about {avg_physics:.3f}; values closer to 1.0 indicate "
                "stronger agreement with the learned DESS artifact signal."
            ),
            (
                f"Stability support averages about {avg_stability:.3f}; this is a supporting signal "
                "for whether the candidate is likely to remain acceptable under the artifact policy."
            ),
            (
                f"Uncertainty averages about {avg_uncertainty:.3f}; higher uncertainty means the model "
                "or artifact prior is less confident and should not be over-interpreted."
            ),
            (
                f"Score source: {', '.join(sources) or 'unknown'}. Artifact matches are stronger evidence "
                "than artifact-calibrated priors for new SMILES."
            ),
        ]

        if ranks:
            interpretation.append(
                "Rank policy combines physics support and stability support, then penalizes uncertainty. "
                "It is designed for prioritization, not final approval."
            )

        caveats = [
            "These scores are screening signals, not experimental validation.",
            (
                "New structures without artifact matches may use a deterministic artifact-calibrated prior "
                "rather than live DESS graph inference."
            ),
            (
                "Use the result to shortlist candidates for deeper chemistry review, not to make a final "
                "formulation decision alone."
            ),
        ]

        recommended_next_steps = [
            "Prioritize candidates with higher rank score and lower uncertainty for the next review pass.",
            "Treat high-uncertainty candidates as requiring additional evidence or manual inspection.",
            "Compare candidate scores against known benchmark molecules or accepted formulations where available.",
            "Capture the selected candidate and explanation in the formulation or experiment dossier.",
        ]

        result = {
            "ai_mode": "offline_explainer",
            "summary": summary,
            "interpretation": interpretation,
            "recommended_next_steps": recommended_next_steps,
            "caveats": caveats,
        }
        result["markdown"] = self._build_markdown(result)
        return result

    def _as_text_list(self, value: Any) -> List[str]:
        """
        Normalize LLM output into a list of readable strings.

        This prevents the common bug where a plain string is treated as an iterable
        and rendered as ["W", "i", "t", "h", ...].
        """
        if value is None:
            return []

        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]

        if isinstance(value, tuple):
            return [str(item).strip() for item in value if str(item).strip()]

        if isinstance(value, str):
            text = value.strip()
            if not text:
                return []

            lines = [
                line.strip(" -•\t")
                for line in text.splitlines()
                if line.strip(" -•\t")
            ]

            if len(lines) > 1:
                return lines

            return [text]

        return [str(value).strip()]

    def _llm_explain(self, payload: Dict[str, Any], mode: str) -> Dict[str, Any]:
        system = (
            "You are a scientific product assistant explaining DESS Bridge scoring outputs to a non-specialist. "
            "Be precise, concise, and conservative. Explain p_physics, stability_support, uncertainty, score_source, and rank_score. "
            "Do not claim experimental validation. Return strict JSON with keys: summary, interpretation, recommended_next_steps, caveats. "
            "The values for interpretation, recommended_next_steps, and caveats must be arrays of strings, not plain strings."
        )

        user = (
            "Explain this DESS Bridge scoring run in plain language. Data:\n"
            + json.dumps(payload, indent=2)[:12000]
        )

        if mode == "deepseek":
            text = self._call_deepseek(system, user)
            ai_mode = f"deepseek:{settings.deepseek_model}"
        else:
            text = self._call_gemini(system, user)
            ai_mode = f"gemini:{settings.gemini_model}"

        parsed = self._parse_llm_json(text)

        result = {
            "ai_mode": ai_mode,
            "summary": str(parsed.get("summary") or "").strip(),
            "interpretation": self._as_text_list(parsed.get("interpretation")),
            "recommended_next_steps": self._as_text_list(parsed.get("recommended_next_steps")),
            "caveats": self._as_text_list(parsed.get("caveats")),
        }

        if not result["summary"]:
            raise ValueError("LLM returned no summary")

        result["markdown"] = self._build_markdown(result)
        return result

    def _call_deepseek(self, system: str, user: str) -> str:
        resp = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.deepseek_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.deepseek_model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
            },
            timeout=45,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def _call_gemini(self, system: str, user: str) -> str:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{settings.gemini_model}:generateContent?key={settings.gemini_api_key}"
        )

        resp = requests.post(
            url,
            json={
                "systemInstruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": user}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "responseMimeType": "application/json",
                },
            },
            timeout=45,
        )
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"]

    def _parse_llm_json(self, text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0 and end > start:
                return json.loads(text[start:end + 1])
            raise

    def _build_markdown(self, data: Dict[str, Any]) -> str:
        lines = [
            "# DESS Bridge run explanation",
            "",
            str(data.get("summary", "")).strip(),
            "",
        ]

        for title, key in [
            ("Interpretation", "interpretation"),
            ("Recommended next steps", "recommended_next_steps"),
            ("Caveats", "caveats"),
        ]:
            items = self._as_text_list(data.get(key))
            if items:
                lines.extend([f"## {title}", ""])
                lines.extend([f"- {item}" for item in items])
                lines.append("")

        return "\n".join(lines).strip() + "\n"
