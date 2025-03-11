from common.astro import Astro, GlobalParams, Moment, Sign
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class TransitParams(GlobalParams):
    planet: str
    sign: str
    sign_index: int
    all: bool
    nakshatra: str
    nakshatra_index: int


@dataclass
class Transits:
    moment: Moment
    sign: Sign


class Transit(Astro):
    def __get(self, params: TransitParams, _sign_index: Optional[int] = None, _nakshatra_index: Optional[int] = None):
        sign_index = _sign_index if _sign_index != None else params.sign_index
        nakshatra_index = _nakshatra_index if _nakshatra_index != None else params.nakshatra_index
        current_time = params.start

        result: List[Transits] = []

        current_sign = ''
        current_nakshatra = ''

        while current_time < params.end:
            jd = self._get_jd(current_time=current_time)
            ayanamsa = self._get_ayanamsa(jd)
            planet_longitude = self._get_planet_longitude(
                planet=params.planet, jd=jd, ayanamsa=ayanamsa)

            sign = self._get_zodiac_sign(planet_longitude)
            if nakshatra_index == -1:
                if sign_index != sign.sign_index:
                    current_sign = ''
                elif sign_index == sign.sign_index and current_sign != sign.name_en and sign.degrees == 0:
                    current_sign = sign.name_en
                    local_time = self._convert_to_local_time(
                        current_time, self.timezone_str)
                    transit = Moment(
                        time=local_time, longitude=planet_longitude)
                    result.append(Transits(moment=transit, sign=sign))
            else:
                _n, _, _ni = self._get_nakshatra(planet_longitude)
                if nakshatra_index != _ni:
                    current_nakshatra = ''
                elif nakshatra_index == _ni and current_nakshatra != _n:
                    current_nakshatra = _n
                    local_time = self._convert_to_local_time(
                        current_time, self.timezone_str)
                    transit = Moment(
                        time=local_time, longitude=planet_longitude)
                    result.append(Transits(moment=transit, sign=sign))

            current_time += params.step

        return result

    def find(self, params: TransitParams,):
        self._set_params(params)
        self._set_global_params()
        results: List[List[Transits]] = []
        if (params.all):
            if params.nakshatra_index != -1:
                for index, _ in enumerate(self.zodiac_signs_en):
                    results.append(self.__get(params, index))
            else:
                for index, _ in enumerate(self.nakshatras):
                    results.append(self.__get(params, 0, index))
        else:
            results.append(self.__get(params))

        return [item for sublist in results for item in sublist]

    def show(self, params: TransitParams):
        self._set_params(params)

        print(
            f"Starting, timezone: {self.timezone_str}, debug: {self.debug}, multiThreading: {self.multiThread}")

        start = datetime.now()

        items: List[Transits] = []

        sign_index = self.find_zodiac_index(params.sign)
        if (sign_index == None):
            print(
                f"Sign is missing: {params.sign}, alloved signs_en:{'|'.join(self.zodiac_signs_en)} \n or signs_ru:{'|'.join(self.zodiac_signs_ru)}")
            exit(1)

        nakshatra_index = -1
        if (params.nakshatra != self.NAKHATRA_DEFAULT):
            _nakshatra_index = self.find_nakshatra_index(params.nakshatra)
            if (_nakshatra_index == None):
                print(
                    f"Nakshatra is missing: {params.nakshatra}, alloved nakshatras:{'|'.join(self.nakshatras)}")
                exit(1)
            nakshatra_index = _nakshatra_index

        if params.multiThread:
            chunks = self.split_dates(
                start=params.start, end=params.end, step=params.step)

            with ProcessPoolExecutor() as executor:
                results = list(executor.map(
                    self.find,
                    [
                        TransitParams(
                            start=chunk.start,
                            end=chunk.end,
                            planet=params.planet,
                            step=params.step,
                            sign=params.sign,
                            multiThread=params.multiThread,
                            maxThreads=params.maxThreads,
                            sign_index=sign_index,
                            all=params.all,
                            nakshatra=params.nakshatra,
                            nakshatra_index=nakshatra_index
                        ) for chunk in chunks
                    ]
                ))

                items = [
                    item for sublist in results for item in sublist]
        else:
            items = self.find(TransitParams(
                start=params.start,
                end=params.end,
                planet=params.planet,
                step=params.step,
                sign=params.sign,
                multiThread=params.multiThread,
                maxThreads=params.maxThreads,
                sign_index=sign_index,
                all=params.all,
                nakshatra=params.nakshatra,
                nakshatra_index=nakshatra_index
            ))

        print(
            f"End for: {datetime.now() - start}")
        if items:
            print(
                f"Moments, when {params.planet} move to sign {params.sign}, from: {params.start}, to: {params.end}, \
for: {params.step}")
            for item in items:
                print(
                    f"Time: {item.moment.time}, Sign: {self._show_sign(sign=item.sign, longitude=item.moment.longitude)}, {params.planet}: {self._show_degres(item.sign)}")
        else:
            print(f"There are no matches for these params: {params}")
