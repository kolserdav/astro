
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class Planet:
    Sun = 'SUN'
    Moon = 'MOON'
    Mercury = 'MERCURY'
    Mars = 'MARS'
    Venus = 'VENUS'
    Saturn = 'SATURN'
    Jupiter = 'JUPITER'
    Rahu = 'TRUE_NODE'
    Ketu = 'KETU'


@dataclass
class Handler:
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

    nakshatras = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashirsha",
        "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
        "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra",
        "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula",
        "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
        "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]

    planet = Planet()

    SIGN_DEFAULT = 'Овен'
    TIME_ZONE_STR_DEFAULT = 'Asia/Krasnoyarsk'
    TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    STEP_MINUTES_DEFAULT = 1
    ACCURACY_DEFAULT = 0.001
    START_DEFAULT = datetime.now()
    END_DEFAULT = datetime.now() + timedelta(days=365)
    THREAD_MAX_DEFAULT: Optional[int] = None
    WITH_TREADS_DEFAULT = True
    DEBUG_DEFAULT = False
    ALL_SIGNS_DEFAULT = False

    def _show_all_planets(self):
        planets = [value for name, value in Planet.__dict__.items(
        ) if not name.startswith('__') and isinstance(value, str)]
        separator = ', '
        result = separator.join(planets)
        print(result)

    def find_zodiac_index(self, sign: str):
        res: Optional[int] = None
        try:
            res = self.zodiac_signs_en.index(sign)
        except ValueError:
            pass

        if (res == None):
            try:
                res = self.zodiac_signs_ru.index(sign)
            except ValueError:
                pass

        if (res == None):
            try:
                res = self.zodiac_signs_sa.index(sign)
            except ValueError:
                pass
        return res

    def _get_nakshatra(self, longitude: float):
        nakshatra_index = int(longitude // 13.3333)
        pada_index = int((longitude % 13.3333) // 3.3333)
        return self.nakshatras[nakshatra_index], pada_index + 1
