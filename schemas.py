from dataclasses import dataclass
from typing import Optional

@dataclass
class Signal:
    type: str                   # username, email, image, post, platform
    value: str                  # the actual value
    confidence: float           # 0.0 - 1.0
    signal_type: str            # FACT or INFERENCE
    evidence: Optional[str] = None
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
