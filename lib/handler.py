
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Handler:
    TIME_ZONE_STR_DEFAULT = 'Asia/Krasnoyarsk'
    TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    STEP_MINUTES_DEFAULT = 1
    ACCURACY_DEFAULT = 0.001
    START_DEFAULT = datetime(2025, 1, 1)
    END_DEFAULT = datetime(2026, 1, 1)
    THREAD_MAX_DEFAULT: Optional[int] = None
    WITH_TREADS_DEFAULT = True
    DEBUG_DEFAULT = False
