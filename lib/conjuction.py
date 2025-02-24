from common.astro import Astro, GlobalParams, Moment, Sign
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class ConjuctionsParams(GlobalParams):
    accuracy: float
    planet1: str
    planet2: str


@dataclass
class Conjuctions:
    planet1: Moment
    planet2: Moment


class Conjuction(Astro):
    def find(self, params: ConjuctionsParams, threadNum: Optional[int] = 1):
        self._set_params(params)

        self._set_global_params()

        if self.debug:
            print(
                f"Start find_planet_conjunctions, thread: {threadNum}: {params}")
        current_time = params.start

        result: List[Conjuctions] = []

        while current_time < params.end:
            jd = self._get_jd(current_time=current_time)
            ayanamsa = swe.get_ayanamsa(jd)  # type: ignore
            planet1_longitude = self._get_planet_longitude(
                planet=params.planet1, jd=jd, ayanamsa=ayanamsa)
            planet2_longitude = self._get_planet_longitude(
                planet=params.planet2, jd=jd, ayanamsa=ayanamsa)

            if abs(planet1_longitude - planet2_longitude) < params.accuracy:
                local_time = self._convert_to_local_time(
                    current_time, self.timezone_str)
                conjuction = Conjuctions(planet1=Moment(
                    time=local_time, longitude=planet1_longitude), planet2=Moment(time=local_time, longitude=planet2_longitude))
                result.append(conjuction)

            current_time += params.step

        return result

    def show(self, params: ConjuctionsParams):
        print(
            f"Starting, timezone: {self.timezone_str}, debug: {self.debug}, multiThread:{params.multiThread}")
        self._set_params(params)

        start = datetime.now()

        conjunctions: List[Conjuctions] = []

        if params.multiThread:
            chunks = self.split_dates(
                start=params.start, end=params.end, step=params.step)

            with ProcessPoolExecutor() as executor:
                results = list(executor.map(
                    self.find,
                    [
                        ConjuctionsParams(
                            start=chunk.start,
                            end=chunk.end,
                            accuracy=params.accuracy,
                            step=params.step,
                            planet1=params.planet1,
                            planet2=params.planet2,
                            multiThread=params.multiThread,
                            maxThreads=params.maxThreads
                        ) for chunk in chunks
                    ]
                ))

                conjunctions = [
                    item for sublist in results for item in sublist]
        else:
            conjunctions = self.find(ConjuctionsParams(
                start=params.start,
                end=params.end,
                accuracy=params.accuracy,
                step=params.step,
                planet1=params.planet1,
                planet2=params.planet2,
                multiThread=params.multiThread,
                maxThreads=params.maxThreads
            ))

        print(
            f"End for: {datetime.now() - start}")
        if conjunctions:
            print(
                f"Moments, when {params.planet1} and {params.planet2} are in one degree, from: {params.start}, to: {params.end}, \
for: {params.step}, with accuracy: {params.accuracy}:")
            for moment in conjunctions:
                time = moment.planet1.time.strftime(self.TIME_FORMAT)
                data1: Sign = self._get_zodiac_sign(moment.planet1.longitude)
                data2: Sign = self._get_zodiac_sign(moment.planet2.longitude)
                print(f"Time: {time}, Sign: {self._show_sign(data1)}, {params.planet1}: {data1.degrees}\
:{data1.minutes}:{data1.seconds}, {params.planet2}: {data2.degrees}:{data2.minutes}:{data2.seconds}")
        else:
            print(f"There are no matches for these params: {params}")
