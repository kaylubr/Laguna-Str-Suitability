import sys
import time

from str_suitability import config
from str_suitability.ingest.load_osm_pbf import snapshot_features

PBF_PATH = config.RAW_DIR / "osm" / "philippines-latest.osm.pbf"
FEATURE_DIR = config.PROJECT_ROOT / "assets" / "osm"

if __name__ == "__main__":
    started = time.time()
    metadata = snapshot_features(PBF_PATH, config.BOUNDARY_DIR, FEATURE_DIR)
    print(f"elapsed: {time.time() - started:.1f}s")
    for key, value in metadata.items():
        print(f"{key}: {value}")
    sys.exit(0)
