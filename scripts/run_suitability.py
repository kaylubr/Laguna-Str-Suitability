import json

from str_suitability import config
from str_suitability.suitability.inputs import load_scoring_input
from str_suitability.suitability.stage import compute_suitability

if __name__ == "__main__":
    scored, report = compute_suitability(load_scoring_input(config.PROCESSED_DIR))

    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    scored.to_parquet(config.PROCESSED_DIR / "grid_suitability.parquet", index=False)
    (config.PROCESSED_DIR / "suitability_summary.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
