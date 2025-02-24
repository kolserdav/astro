from common.astro import Astro, GlobalParams, Moment, Sign
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass


@dataclass
class PlanetParams:
    all: bool


class Planet(Astro):
    def show(self, args: PlanetParams):
        if (args.all):
            self._show_all_planets()
