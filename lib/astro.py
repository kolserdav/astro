from typing import List, Optional
from concurrent.futures import ProcessPoolExecutor
import swisseph as swe
from datetime import datetime, timedelta
import pytz
from dataclasses import dataclass
import os


@dataclass
class Planet():
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
    debug: Optional[bool] = False


@dataclass
class Astro:

    multiThread = False

    EPOCH = datetime(1970, 1, 1)

    CPUS = os.cpu_count()

    planet = Planet()

    timezone_str: str

    debug = True

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

    @classmethod
    def __init__(cls, timezone_str: str, debug: Optional[bool] = False):
        cls.timezone_str = timezone_str
        cls.debug = debug

        swe.set_ephe_path('./swisseph/ephe')  # type: ignore
        swe.set_sid_mode(swe.SIDM_LAHIRI)  # type: ignore

    @classmethod
    def convert_to_local_time(cls, utc_time, timezone_str) -> datetime:
        timezone = pytz.timezone(timezone_str)
        local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(timezone)
        return local_time

    @classmethod
    def set_conjuction_params(cls, params: ConjuctionsParams):
        cls.debug = params.debug
        cls.multiThread = params.multiThread

    @classmethod
    def get_zodiac_sign(cls, longitude) -> Sign:
        sign_index = int(longitude // 30)
        degree_in_sign = longitude % 30

        degrees = int(degree_in_sign)
        minutes = int((degree_in_sign - degrees) * 60)
        seconds = ((degree_in_sign - degrees) * 60 - minutes) * 60
        return Sign(
            name_en=cls.zodiac_signs_en[sign_index],
            name_ru=cls.zodiac_signs_ru[sign_index],
            name_sa=cls.zodiac_signs_sa[sign_index],
            degrees=degrees,
            minutes=minutes,
            seconds=round(seconds, 1)
        )

    @classmethod
    def find_planet_conjunctions(cls, params: ConjuctionsParams, threadNum: Optional[int] = 1):
        cls.set_conjuction_params(params)
        if cls.debug:
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
                swe, params.planet1) if params.planet1 != cls.planet.Ketu else getattr(swe, cls.planet.Rahu)
            planet2_value = getattr(
                swe, params.planet2) if params.planet2 != cls.planet.Ketu else getattr(swe, cls.planet.Rahu)
            planet1_data = swe.calc(jd, planet1_value)  # type: ignore
            planet2_data = swe.calc(jd, planet2_value)  # type: ignore

            shift1 = 0 if params.planet1 != cls.planet.Ketu else 180
            shift2 = 0 if params.planet2 != cls.planet.Ketu else 180

            ayanamsa = swe.get_ayanamsa(jd)  # type: ignore

            planet1_longitude = swe.degnorm(  # type: ignore
                planet1_data[0][0] + shift1 - ayanamsa)
            planet2_longitude = swe.degnorm(  # type: ignore
                planet2_data[0][0] + shift2 - ayanamsa)

            if abs(planet1_longitude - planet2_longitude) < params.accuracy:
                local_time = cls.convert_to_local_time(
                    current_time, cls.timezone_str)
                conjuction = Conjuctions(planet1=Conjuction(
                    time=local_time, longitude=planet1_longitude), planet2=Conjuction(time=local_time, longitude=planet2_longitude))
                result.append(conjuction)

            current_time += params.step

        if cls.debug:
            print(
                f"End find_planet_conjunctions, thread: {threadNum}: {params}")

        return result

    @classmethod
    def split_dates(cls, start: datetime, end: datetime, step: timedelta):
        cpus = cls.CPUS if cls.CPUS != None else 4
        total_seconds_start = (start - cls.EPOCH).total_seconds()
        total_seconds_end = (end - cls.EPOCH).total_seconds()
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

    @classmethod
    def show_conjuctions(cls, params: ConjuctionsParams):
        cls.set_conjuction_params(params)

        start = datetime.now()

        conjunctions: List[Conjuctions] = []

        if params.multiThread:
            chunks = cls.split_dates(
                start=params.start, end=params.end, step=params.step)

            with ProcessPoolExecutor() as executor:
                results = list(executor.map(
                    cls.find_planet_conjunctions,
                    [
                        ConjuctionsParams(
                            start=chunk.start,
                            end=chunk.end,
                            accuracy=params.accuracy,
                            step=params.step,
                            planet1=params.planet1,
                            planet2=params.planet2,
                            debug=params.debug,
                        ) for chunk in chunks
                    ]
                ))

                conjunctions = [
                    item for sublist in results for item in sublist]
        else:
            conjunctions = cls.find_planet_conjunctions(ConjuctionsParams(
                start=params.start,
                end=params.end,
                accuracy=params.accuracy,
                step=params.step,
                planet1=params.planet1,
                planet2=params.planet2,
                debug=params.debug,
            ))

        print(
            f"End for: {datetime.now() - start}, multiThread:{params.multiThread}")
        if conjunctions:
            print(
                f"Moments, when {params.planet1} and {params.planet2} are in one degree, from: {params.start}, to: {params.end}, \
for: {params.step}, with accuracy: {params.accuracy}:")
            for moment in conjunctions:
                time = moment.planet1.time.strftime("%Y-%m-%d %H:%M:%S")
                data1: Sign = cls.get_zodiac_sign(moment.planet1.longitude)
                data2: Sign = cls.get_zodiac_sign(moment.planet2.longitude)
                print(f"Time: {time}, Sign: {data1.name_ru}|{data1.name_en}|{data1.name_sa}, {params.planet1}: {data1.degrees}\
:{data1.minutes}:{data1.seconds}, {params.planet2}: {data2.degrees}:{data2.minutes}:{data2.seconds}")
        else:
            print("There are no matches for these params")
