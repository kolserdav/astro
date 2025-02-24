from common.astro import Astro, GlobalParams, Moment, Sign
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class RetroParams(GlobalParams):
    planet: str


@dataclass
class Retros:
    moment: Moment
    sign: Sign
    out: bool


class Retro(Astro):
    def get(self, params: RetroParams):
        current_time = params.start

        result: List[Retros] = []

        previous_longitude: Optional[float] = None

        retro_started = False

        retro_ended = False

        while current_time < params.end:
            jd = self._get_jd(current_time=current_time)
            ayanamsa = self._get_ayanamsa(jd)
            planet_longitude = self._get_planet_longitude(
                planet=params.planet, jd=jd, ayanamsa=ayanamsa)

            if previous_longitude is not None:
                if (planet_longitude < previous_longitude and
                        ((previous_longitude - planet_longitude) < 180) and not retro_started):
                    if (retro_ended):
                        sign = self._get_zodiac_sign(
                            longitude=planet_longitude)
                        result.append(Retros(
                            sign=sign,
                            out=False,
                            moment=Moment(
                                longitude=planet_longitude, time=current_time)
                        ))
                    retro_started = True
                    retro_ended = False
                elif ((planet_longitude > previous_longitude) and
                        not retro_ended):
                    if (retro_started):
                        sign = self._get_zodiac_sign(
                            longitude=planet_longitude)
                        result.append(Retros(
                            sign=sign,
                            out=True,
                            moment=Moment(
                                longitude=planet_longitude, time=current_time)
                        ))
                    retro_ended = True
                    retro_started = False

            previous_longitude = planet_longitude

            current_time += params.step

        return result

    def show(self, params: RetroParams):
        self._set_params(params)

        print(
            f"Starting, timezone: {self.timezone_str}, debug: {self.debug}, multiThreading: {self.multiThread}")

        start = datetime.now()

        items: List[Retros] = []

        if params.multiThread:
            chunks = self.split_dates(
                start=params.start, end=params.end, step=params.step)

            with ProcessPoolExecutor() as executor:
                results = list(executor.map(
                    self.get,
                    [
                        RetroParams(
                            start=chunk.start,
                            end=chunk.end,
                            planet=params.planet,
                            step=params.step,
                            multiThread=params.multiThread,
                            maxThreads=params.maxThreads,
                        ) for chunk in chunks
                    ]
                ))

                items = [
                    item for sublist in results for item in sublist]
        else:
            items = self.get(RetroParams(
                start=params.start,
                end=params.end,
                planet=params.planet,
                step=params.step,
                multiThread=params.multiThread,
                maxThreads=params.maxThreads,
            ))

        print(
            f"End for: {datetime.now() - start}")
        if items:
            print(
                f"Moments, when {params.planet} is starting or stoppind retro: {params.start}, to: {params.end}, \
for: {params.step}")
            for item in items:
                print(
                    f"Time: {item.moment.time}, Retro is: {not item.out} Sign: {self._show_sign(item.sign)}, {params.planet}: {self._show_degres(item.sign)}")
        else:
            print(f"There are no matches for these params: {params}")
