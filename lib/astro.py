from typing import List, Optional
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
class Conjuction:
    time: datetime
    longitude: float


@dataclass
class Conjuctions:
    planet1: Conjuction
    planet2: Conjuction


@dataclass
class Sign:
    name_en: str
    name_ru: str
    name_sa: str
    degrees: int
    minutes: int
    seconds: float


@dataclass
class TimeRange:
    start: datetime
    end: datetime


@dataclass
class ConjuctionsParams:
    start: datetime
    end: datetime
    step: timedelta
    accuracy: float
    planet1: str
    planet2: str
    multiThread: Optional[bool] = False
    maxThreads: Optional[int] = None


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

    zodiac_signs_ru = [
        "Овен", "Телец", "Близнецы", "Рак",
        "Лев", "Дева", "Весы", "Скорпион",
        "Стрелец", "Козерог", "Водолей", "Рыбы"
    ]

    zodiac_signs_sa = [
        "Меша", "Вṛишабха", "Мithун", "Карк",
        "Сiṃха", "Кanyа", "Тuлa", "Vрiśćика",
        "Дhanu", "Mакара", "Кumbha", "Mīна"
    ]

    zodiac_signs_en = [
        "Aries", "Taurus", "Gemini", "Cancer",
        "Leo", "Virgo", "Libra", "Scorpio",
        "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]

    def __init__(self, timezone_str: str, debug: Optional[bool] = False):
        self.timezone_str = timezone_str
        self.debug = debug

    def convert_to_local_time(self, utc_time, timezone_str) -> datetime:
        timezone = pytz.timezone(timezone_str)
        local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(timezone)
        return local_time

    def set_conjuction_params(self, params: ConjuctionsParams):
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
            seconds=round(seconds, 1)
        )

    def find_planet_conjunctions(self, params: ConjuctionsParams, threadNum: Optional[int] = 1):
        self.set_conjuction_params(params)

        swe.set_ephe_path(self.EPHE_PATH)  # type: ignore
        swe.set_sid_mode(swe.SIDM_LAHIRI)  # type: ignore

        if self.debug:
            print(
                f"Start find_planet_conjunctions, thread: {threadNum}: {params}")
        current_time = params.start

        result: List[Conjuctions] = []

        while current_time < params.end:
            jd = swe.utc_to_jd(  # type: ignore
                current_time.year,
                current_time.month,
                current_time.day,
                current_time.hour,
                current_time.minute,
                current_time.second,
                swe.GREG_CAL)[1]  # type: ignore
            planet1_value = getattr(
                swe, params.planet1) if params.planet1 != self.planet.Ketu else getattr(swe, self.planet.Rahu)
            planet2_value = getattr(
                swe, params.planet2) if params.planet2 != self.planet.Ketu else getattr(swe, self.planet.Rahu)
            planet1_data = swe.calc(jd, planet1_value)  # type: ignore
            planet2_data = swe.calc(jd, planet2_value)  # type: ignore

            shift1 = 0 if params.planet1 != self.planet.Ketu else 180
            shift2 = 0 if params.planet2 != self.planet.Ketu else 180

            ayanamsa = swe.get_ayanamsa(jd)  # type: ignore

            planet1_longitude = swe.degnorm(  # type: ignore
                planet1_data[0][0] + shift1 - ayanamsa)
            planet2_longitude = swe.degnorm(  # type: ignore
                planet2_data[0][0] + shift2 - ayanamsa)

            if abs(planet1_longitude - planet2_longitude) < params.accuracy:
                local_time = self.convert_to_local_time(
                    current_time, self.timezone_str)
                conjuction = Conjuctions(planet1=Conjuction(
                    time=local_time, longitude=planet1_longitude), planet2=Conjuction(time=local_time, longitude=planet2_longitude))
                result.append(conjuction)

            current_time += params.step

        if self.debug:
            print(
                f"End find_planet_conjunctions, thread: {threadNum}: {params}")

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

    def show_conjuctions(self, params: ConjuctionsParams):
        print(f"Starting, timezone: {self.timezone_str}, debug: {self.debug}")
        self.set_conjuction_params(params)

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
            print("There are no matches for these params")
