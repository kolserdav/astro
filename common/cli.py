from argparse import ArgumentParser
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
from common.handler import Handler


@dataclass
class ArgsCommon:
    command: Optional[str]
    step: Optional[int]
    start: Optional[str]
    end: Optional[str]
    threads_max:  Optional[int]
    no_threads: Optional[bool]


@dataclass
class ArgsConjuctionParsed(ArgsCommon):
    accuracy: Optional[float]
    planet1: Optional[str]
    planet2: Optional[str]


@dataclass
class ArgsTransitParsed(ArgsCommon):
    planet: Optional[str]
    sign: Optional[str]
    all: Optional[bool]
    nakshatra: Optional[str]


@dataclass
class ArgsRetroParsed(ArgsCommon):
    planet: Optional[str]


@dataclass
class ArgsPlanetsParsed:
    all: Optional[bool]


@dataclass
class Cli(Handler):
    _subparsers: Optional[Any] = None

    PERFORMANCE_MESS = 'PERFORMANCE'

    ACCURACY_MESS = 'ACCURACY'

    COMMAND_CONJUCTION = 'conjuction'

    COMMAND_TRANSIT = 'transit'

    COMMAND_RETRO = 'retro'

    COMMAND_PLANETS = 'planet'

    command = ''
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    args_conjuction = ArgsConjuctionParsed(
        command=None,
        start=None,
        end=None,
        step=None,
        accuracy=None,
        no_threads=None,
        threads_max=None,
        planet1=None,
        planet2=None
    )

    args_transit = ArgsTransitParsed(
        command=None,
        start=None,
        end=None,
        step=None,
        no_threads=None,
        threads_max=None,
        planet=None,
        sign=None,
        all=None,
        nakshatra=None
    )

    args_retro = ArgsRetroParsed(
        command=None,
        start=None,
        end=None,
        step=None,
        no_threads=None,
        threads_max=None,
        planet=None,
    )

    args_planets = ArgsPlanetsParsed(
        all=None
    )

    def argparse(self):
        parser = ArgumentParser(description='Astro compute utility')
        self._subparsers = parser.add_subparsers(
            title='Commands', dest='command')

        subparser = self.__set_conjuction_args()
        self.set_common_args(subparser=subparser)

        subparser = self.__set_transit_args()
        self.set_common_args(subparser=subparser)

        subparser = self.__set_retro_args()
        self.set_common_args(subparser=subparser)

        subparser = self.__set_planets_args()

        args: Any = parser.parse_args()

        self.command = args.command

        if (self.command == None):
            print(f"Command is not passed, try add -h|-help parameter")

        if (self.command == self.COMMAND_CONJUCTION):
            self.args_conjuction = args
            self._cast_args(args)
        elif (self.command == self.COMMAND_TRANSIT):
            self.args_transit = args
            self._cast_args(args)
        elif (self.command == self.COMMAND_RETRO):
            self.args_retro = args
            self._cast_args(args)
        elif (self.command == self.COMMAND_PLANETS):
            self.args_planets = args

    def __get_clean_time_format(self):
        return str(self.TIME_FORMAT).replace('%', '')

    def __set_retro_args(self):
        if (self._subparsers == None):
            print(f"Subparser is None in __set_retro_args")
            return

        subparser = self._subparsers.add_parser(
            name=self.COMMAND_RETRO, description='Get planet retro')

        subparser.add_argument('-p', '--planet', type=str,
                               help=f"Planet: str [SUN]", required=False)

        return subparser

    def __set_planets_args(self):
        if (self._subparsers == None):
            print(f"Subparser is None in __set_planets_args")
            return

        subparser = self._subparsers.add_parser(
            name=self.COMMAND_PLANETS, description='Planet info')

        subparser.add_argument('-a', '--all', action='store_true',
                               help=f"Show all supported planets: bool", required=False)

        return subparser

    def __set_transit_args(self):
        if (self._subparsers == None):
            print(f"Subparser is None in _set_transit_args")
            return

        subparser = self._subparsers.add_parser(
            name=self.COMMAND_TRANSIT, description='Get planet transit')

        subparser.add_argument(
            '--sign', type=str, help=f"Target sign: str [{self.zodiac_signs_en[0]}]", required=False)
        subparser.add_argument('-p', '--planet', type=str,
                               help=f"Planet: str [SUN]", required=False)
        subparser.add_argument('-a', '--all', action='store_true',
                               help=f"All signs: bool [{self.ALL_SIGNS_DEFAULT == False}]", required=False)
        subparser.add_argument('-n', '--nakshatra',  type=str,
                               help=f"Nakshatra name: str [None]", required=False)

        return subparser

    def __set_conjuction_args(self):
        if (self._subparsers == None):
            print(f"Subparser is None in _set_conjuction_args")
            return
        subparser = self._subparsers.add_parser(
            name=self.COMMAND_CONJUCTION, description='Get planet conjuctions')

        subparser.add_argument('-a', '--accuracy', type=float,
                               help=f"Degrees conjuction accuracy: float [{self.ACCURACY_DEFAULT}]", required=False)
        subparser.add_argument('-p1', '--planet1', type=str,
                               help=f"Planet 1: str [SUN]", required=False)
        subparser.add_argument('-p2', '--planet2', type=str,
                               help=f"Planet 2: str [MOON]", required=False)
        return subparser

    def set_common_args(self, subparser: Any):
        time_format = self.__get_clean_time_format()
        subparser.add_argument(
            '--start', type=str, help=f"Start date: str '{time_format}' [{self.START_DEFAULT}]", required=False)
        subparser.add_argument(
            '-e', '--end', type=str, help=f"End date: str '{time_format}' [{self.END_DEFAULT}]", required=False)
        subparser.add_argument('--no-threads', action='store_true',
                               help=f"Without multithreading ({self.PERFORMANCE_MESS}): bool [{self.WITH_TREADS_DEFAULT == False}]", required=False)
        subparser.add_argument(
            '--threads-max', type=int, help=f"Threads max ({self.PERFORMANCE_MESS}): int [{self.THREAD_MAX_DEFAULT}]", required=False)
        subparser.add_argument(
            '-s', '--step', type=int, help=f"Step in minutes ({self.PERFORMANCE_MESS}/{self.ACCURACY_MESS}): int [{self.STEP_MINUTES_DEFAULT}]", required=False)

    def _cast_args(self, args: ArgsCommon):
        if args.start != None:
            try:
                self.start = datetime.strptime(args.start, self.TIME_FORMAT)
            except Exception as e:
                print(f"Failed parse argument --start: {e}")
                exit(1)

        if args.end != None:
            try:
                self.end = datetime.strptime(args.end, self.TIME_FORMAT)
            except Exception as e:
                print(f"Failed parse argument -e|--end: {e}")
                exit(1)
