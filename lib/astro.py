from typing import List, Optional, Any
from concurrent.futures import ProcessPoolExecutor
import swisseph as swe
from datetime import datetime, timedelta
import pytz
from dataclasses import dataclass
import os
from lib.handler import Handler


@dataclass
class Planet(Handler):
    Sun = 'SUN'
    Moon = 'MOON'
    Mercury = 'MERCURY'
    Rahu = 'TRUE_NODE'
    Ketu = 'KETU'


@dataclass
class Moment:
    time: datetime
    longitude: float


@dataclass
class Conjuctions:
    planet1: Moment
    planet2: Moment


@dataclass
class Sign:
    name_en: str
    name_ru: str
    name_sa: str
    degrees: int
    minutes: int
    seconds: float
    sign_index: int


@dataclass
class Transits:
    moment: Moment
    sign: Sign


@dataclass
class TimeRange:
    start: datetime
    end: datetime


@dataclass
class GlobalParams:
    multiThread: Optional[bool]
    maxThreads: Optional[int]


@dataclass
class ConjuctionsParams(GlobalParams):
    start: datetime
    end: datetime
    step: timedelta
    accuracy: float
    planet1: str
    planet2: str


@dataclass
class TransitParams(GlobalParams):
    start: datetime
    end: datetime
    step: timedelta
    planet: str
    sign: str
    sign_index: int


@dataclass
class Astro(Handler):

    EPHE_PATH = './swisseph/ephe'

    multiThread = False

    EPOCH = datetime(1970, 1, 1)

    CPUS = os.cpu_count()

    planet = Planet()

    timezone_str: str = Handler.TIME_ZONE_STR_DEFAULT

    debug = True

    max_threads: Optional[int] = None

    def __init__(self, timezone_str: str, debug: Optional[bool] = False):
        self.timezone_str = timezone_str
        self.debug = debug

    def convert_to_local_time(self, utc_time, timezone_str) -> datetime:
        timezone = pytz.timezone(timezone_str)
        local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(timezone)
        return local_time

    def set_params(self, params: GlobalParams):
        self.multiThread = params.multiThread
        self.max_threads = params.maxThreads

    def get_zodiac_sign(self, longitude) -> Sign:
        sign_index = int(longitude // 30)
        degree_in_sign = longitude % 30

        degrees = int(degree_in_sign)
        minutes = int((degree_in_sign - degrees) * 60)
        seconds = ((degree_in_sign - degrees) * 60 - minutes) * 60
        return Sign(
            name_en=self.zodiac_signs_en[sign_index],
            name_ru=self.zodiac_signs_ru[sign_index],
            name_sa=self.zodiac_signs_sa[sign_index],
            degrees=degrees,
            minutes=minutes,
            seconds=round(seconds, 1),
            sign_index=sign_index
        )

    def __set_global_params(self):
        swe.set_ephe_path(self.EPHE_PATH)  # type: ignore
        swe.set_sid_mode(swe.SIDM_LAHIRI)  # type: ignore

    def __get_jd(self, current_time: datetime):
        return swe.utc_to_jd(  # type: ignore
            current_time.year,
            current_time.month,
            current_time.day,
            current_time.hour,
            current_time.minute,
            current_time.second,
            swe.GREG_CAL)[1]  # type: ignore

    def __get_planet_value(self, planet: str):
        return getattr(
            swe, planet) if planet != self.planet.Ketu else getattr(swe, self.planet.Rahu)

    def __get_planet_longitude(self, planet: str, jd: Any, ayanamsa: Any) -> float:
        planet_value = self.__get_planet_value(planet)
        planet_data = swe.calc(jd, planet_value)  # type: ignore
        shift = 0 if planet != self.planet.Ketu else 180
        return swe.degnorm(  # type: ignore
            planet_data[0][0] + shift - ayanamsa)

    def find_planet_conjunctions(self, params: ConjuctionsParams, threadNum: Optional[int] = 1):
        self.set_params(params)

        self.__set_global_params()

        if self.debug:
            print(
                f"Start find_planet_conjunctions, thread: {threadNum}: {params}")
        current_time = params.start

        result: List[Conjuctions] = []

        while current_time < params.end:
            jd = self.__get_jd(current_time=current_time)
            ayanamsa = swe.get_ayanamsa(jd)  # type: ignore
            planet1_longitude = self.__get_planet_longitude(
                planet=params.planet1, jd=jd, ayanamsa=ayanamsa)
            planet2_longitude = self.__get_planet_longitude(
                planet=params.planet2, jd=jd, ayanamsa=ayanamsa)

            if abs(planet1_longitude - planet2_longitude) < params.accuracy:
                local_time = self.convert_to_local_time(
                    current_time, self.timezone_str)
                conjuction = Conjuctions(planet1=Moment(
                    time=local_time, longitude=planet1_longitude), planet2=Moment(time=local_time, longitude=planet2_longitude))
                result.append(conjuction)

            current_time += params.step

        return result

    def find_planet_transit(self, params: TransitParams, threadNum: Optional[int] = 1):
        self.set_params(params)

        self.__set_global_params()

        if self.debug:
            print(
                f"Start find_planet_conjunctions, thread: {threadNum}: {params}")
        current_time = params.start

        result: List[Transits] = []

        current_sign = ''

        while current_time < params.end:
            jd = self.__get_jd(current_time=current_time)
            ayanamsa = swe.get_ayanamsa(jd)  # type: ignore
            planet_longitude = self.__get_planet_longitude(
                planet=params.planet, jd=jd, ayanamsa=ayanamsa)

            sign = self.get_zodiac_sign(planet_longitude)

            if params.sign_index != sign.sign_index:
                current_sign = ''
            elif params.sign_index == sign.sign_index and current_sign != sign.name_en and sign.degrees == 0:
                current_sign = sign.name_en
                local_time = self.convert_to_local_time(
                    current_time, self.timezone_str)
                transit = Moment(
                    time=local_time, longitude=planet_longitude)
                result.append(Transits(moment=transit, sign=sign))

            current_time += params.step

        if self.debug:
            print(
                f"End find_planet_transit, thread: {threadNum}: {params}")
        return result

    def split_dates(self, start: datetime, end: datetime, step: timedelta):
        cpus = self.CPUS if self.CPUS != None else 4
        cpus = self.max_threads if self.max_threads != None and cpus > self.max_threads else cpus

        total_seconds_start = (start - self.EPOCH).total_seconds()
        total_seconds_end = (end - self.EPOCH).total_seconds()
        total_seconds_step = (step).total_seconds()
        number_of_timedeltas = int((
            total_seconds_end - total_seconds_start) // total_seconds_step)
        chunk_length = max(1, number_of_timedeltas //
                           cpus) * total_seconds_step

        res: List[TimeRange] = []
        for i in range(cpus):
            current_start = start + timedelta(seconds=i * chunk_length)
            current_end = current_start + timedelta(seconds=chunk_length)

            if current_end > end:
                current_end = end

            res.append(TimeRange(start=current_start, end=current_end))

        return res

    def show_transits(self, params: TransitParams):
        print(f"Starting, timezone: {self.timezone_str}, debug: {self.debug}")
        self.set_params(params)

        start = datetime.now()

        transits: List[Transits] = []

        sign_index = self.find_zodiac_index(params.sign)
        if (sign_index == None):
            print(
                f"Sign is missing: {params.sign}, alloved signs_en:{'|'.join(self.zodiac_signs_en)} \n or signs_ru:{'|'.join(self.zodiac_signs_ru)}")
            exit(1)

        if params.multiThread:
            chunks = self.split_dates(
                start=params.start, end=params.end, step=params.step)

            with ProcessPoolExecutor() as executor:
                results = list(executor.map(
                    self.find_planet_transit,
                    [
                        TransitParams(
                            start=chunk.start,
                            end=chunk.end,
                            planet=params.planet,
                            step=params.step,
                            sign=params.sign,
                            multiThread=params.multiThread,
                            maxThreads=params.maxThreads,
                            sign_index=sign_index
                        ) for chunk in chunks
                    ]
                ))

                transits = [
                    item for sublist in results for item in sublist]
        else:
            transits = self.find_planet_transit(TransitParams(
                start=params.start,
                end=params.end,
                planet=params.planet,
                step=params.step,
                sign=params.sign,
                multiThread=params.multiThread,
                maxThreads=params.maxThreads,
                sign_index=sign_index
            ))

        print(
            f"End for: {datetime.now() - start}, multiThread:{params.multiThread}")
        if transits:
            print(
                f"Moments, when {params.planet} move to sign {params.sign}, from: {params.start}, to: {params.end}, \
for: {params.step}")
            for transit in transits:
                print(f"Time: {transit.moment.time}, Sign: {transit.sign.name_ru}|{transit.sign.name_en}|{transit.sign.name_sa}, {params.planet}: {transit.sign.degrees}\
:{transit.sign.minutes}:{transit.sign.seconds}")
        else:
            print(f"There are no matches for these params: {params}")

    def show_conjuctions(self, params: ConjuctionsParams):
        print(f"Starting, timezone: {self.timezone_str}, debug: {self.debug}")
        self.set_params(params)

        start = datetime.now()

        conjunctions: List[Conjuctions] = []

        if params.multiThread:
            chunks = self.split_dates(
                start=params.start, end=params.end, step=params.step)

            with ProcessPoolExecutor() as executor:
                results = list(executor.map(
                    self.find_planet_conjunctions,
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
            conjunctions = self.find_planet_conjunctions(ConjuctionsParams(
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
            f"End for: {datetime.now() - start}, multiThread:{params.multiThread}")
        if conjunctions:
            print(
                f"Moments, when {params.planet1} and {params.planet2} are in one degree, from: {params.start}, to: {params.end}, \
for: {params.step}, with accuracy: {params.accuracy}:")
            for moment in conjunctions:
                time = moment.planet1.time.strftime(self.TIME_FORMAT)
                data1: Sign = self.get_zodiac_sign(moment.planet1.longitude)
                data2: Sign = self.get_zodiac_sign(moment.planet2.longitude)
                print(f"Time: {time}, Sign: {data1.name_ru}|{data1.name_en}|{data1.name_sa}, {params.planet1}: {data1.degrees}\
:{data1.minutes}:{data1.seconds}, {params.planet2}: {data2.degrees}:{data2.minutes}:{data2.seconds}")
        else:
            print(f"There are no matches for these params: {params}")
