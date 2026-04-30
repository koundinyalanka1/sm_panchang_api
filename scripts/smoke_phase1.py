from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.main import calculate_panchang
from app.models import PanchangRequest


def main() -> None:
    payload_path = PROJECT_ROOT / "examples" / "phase1_request.json"
    payload = json.loads(payload_path.read_text())
    response = calculate_panchang(PanchangRequest.model_validate(payload))
    print(response.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
