from typing import List, Optional, Any
from concurrent.futures import ProcessPoolExecutor
import swisseph as swe
from datetime import datetime, timedelta
import pytz
from dataclasses import dataclass
import os
from common.handler import Handler


@dataclass
class Moment:
    time: datetime
    longitude: float


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
class TimeRange:
    start: datetime
    end: datetime


@dataclass
class GlobalParams:
    start: datetime
    end: datetime
    step: timedelta
    multiThread: Optional[bool]
    maxThreads: Optional[int]


@dataclass
class Astro(Handler):

    EPHE_PATH = './swisseph/ephe'

    multiThread = False

    EPOCH = datetime(1970, 1, 1)

    CPUS = os.cpu_count()

    timezone_str: str = Handler.TIME_ZONE_STR_DEFAULT

    debug = True

    max_threads: Optional[int] = None

    def __init__(self, timezone_str: str, debug: Optional[bool] = False):
        self.timezone_str = timezone_str
        self.debug = debug

    def _convert_to_local_time(self, utc_time, timezone_str) -> datetime:
        timezone = pytz.timezone(timezone_str)
        local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(timezone)
        return local_time

    def _set_params(self, params: GlobalParams):
        self.multiThread = params.multiThread
        self.max_threads = params.maxThreads

    def _get_zodiac_sign(self, longitude) -> Sign:
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

    def _set_global_params(self):
        swe.set_ephe_path(self.EPHE_PATH)  # type: ignore
        swe.set_sid_mode(swe.SIDM_LAHIRI)  # type: ignore

    def _get_jd(self, current_time: datetime):
        return swe.utc_to_jd(  # type: ignore
            current_time.year,
            current_time.month,
            current_time.day,
            current_time.hour,
            current_time.minute,
            current_time.second,
            swe.GREG_CAL)[1]  # type: ignore

    def _get_planet_value(self, planet: str):
        return getattr(
            swe, planet) if planet != self.planet.Ketu else getattr(swe, self.planet.Rahu)

    def _get_planet_longitude(self, planet: str, jd: Any, ayanamsa: Any) -> float:
        planet_value = self._get_planet_value(planet)
        planet_data = swe.calc(jd, planet_value)  # type: ignore
        shift = 0 if planet != self.planet.Ketu else 180
        return swe.degnorm(  # type: ignore
            planet_data[0][0] + shift - ayanamsa)

    def _get_ayanamsa(self, jd: Any):
        return swe.get_ayanamsa(jd)  # type: ignore

    def _show_sign(self, sign: Sign, longitude: float):
        nakshatra, pada, _ = self._get_nakshatra(longitude=longitude)
        return f"{sign.name_ru}|{sign.name_en}|{sign.name_sa}:{sign.sign_index + 1}:{nakshatra}({pada})"

    def _show_degres(self, sign: Sign):
        return f"{sign.degrees}:{sign.minutes}:{sign.seconds}"

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
