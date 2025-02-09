from lib.astro import Astro, ConjuctionsParams
from datetime import datetime, timedelta

astro = Astro(timezone_str='Asia/Krasnoyarsk')

astro.show_conjuctions(
    ConjuctionsParams(
        start=datetime(2025, 4, 1),
        end=datetime(2026, 3, 1),
        step=timedelta(minutes=1),
        accuracy=0.001,
        planet1=astro.planet.Moon,
        planet2=astro.planet.Ketu,
        multiThread=False,
        debug=True
    )
)
