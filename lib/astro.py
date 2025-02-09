from typing import List
import swisseph as swe
from datetime import datetime, timedelta
import pytz
from dataclasses import dataclass

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
class Astro:
    planet = Planet()

    timezone_str: str

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
    def __init__(cls, timezone_str: str):       
        cls.timezone_str = timezone_str
        
        swe.set_ephe_path('./swisseph/ephe')
        swe.set_sid_mode(swe.SIDM_LAHIRI)

    @classmethod
    def convert_to_local_time(cls, utc_time, timezone_str) -> datetime:
        timezone = pytz.timezone(timezone_str)
        local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(timezone)
        return local_time
    
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
    def find_planets_conjunction(cls, start: datetime, end: datetime, step: timedelta, accuracy:float, planet1: str, planet2: str):
        current_time = start

        conjunctions: List[Conjuctions] = []
       
        while current_time < end:
            jd = swe.utc_to_jd(current_time.year, current_time.month, current_time.day,
                               current_time.hour, current_time.minute, current_time.second, swe.GREG_CAL)[1]
            planet1_value = getattr(swe, planet1) if planet1 != cls.planet.Ketu else getattr(swe, cls.planet.Rahu)
            planet2_value = getattr(swe, planet2) if planet2 != cls.planet.Ketu else getattr(swe, cls.planet.Rahu)
            planet1_data = swe.calc(jd, planet1_value)
            planet2_data = swe.calc(jd, planet2_value)
            
            shift1 = 0 if planet1 != cls.planet.Ketu else 180
            shift2= 0 if planet2 != cls.planet.Ketu else 180

            ayanamsa = swe.get_ayanamsa(jd)

            planet1_longitude = swe.degnorm(planet1_data[0][0] + shift1 - ayanamsa)
            planet2_longitude = swe.degnorm(planet2_data[0][0] + shift2 - ayanamsa)
            
            if abs(planet1_longitude - planet2_longitude) < accuracy:
                local_time = cls.convert_to_local_time(current_time, cls.timezone_str)
                conjunctions.append(Conjuctions(planet1=Conjuction(time=local_time, longitude=planet1_longitude), planet2=Conjuction(time=local_time, longitude=planet2_longitude)))
            
            current_time += step
        
        return conjunctions

    @classmethod
    def show_conjuctions(cls, start: datetime, end: datetime, step: timedelta, accuracy: float, planet1: str, planet2: str):
        conjunctions = cls.find_planets_conjunction(start=start, end=end, step=step, accuracy=accuracy, planet1=planet1, planet2=planet2)
        if conjunctions:
            print(f"Moments, when {planet1} and {planet2} are in one degree, from: {start}, to: {end}, for: {step}, with accuracy: {accuracy}:")
            for moment in conjunctions:
                time = moment.planet1.time.strftime("%Y-%m-%d %H:%M:%S")
                data1: Sign = cls.get_zodiac_sign(moment.planet1.longitude)
                data2: Sign = cls.get_zodiac_sign(moment.planet2.longitude)
                print(f"Time: {time}, Sign: {data1.name_ru}|{data1.name_en}|{data1.name_sa}, {planet1}: {data1.degrees}:{data1.minutes}:{data1.seconds}, {planet2}: {data2.degrees}:{data2.minutes}:{data2.seconds}")
        else:
            print("There are no matches for these params")

