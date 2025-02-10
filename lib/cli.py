from argparse import ArgumentParser
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
from lib.handler import Handler

@dataclass
class ArgsParsed:
    command: Optional[str]
    start: Optional[str]
    end: Optional[str]
    step: Optional[int]
    accuracy: Optional[float]
    no_threads: Optional[bool]
    threads_max:  Optional[int]
    planet1: Optional[str]
    planet2: Optional[str]

@dataclass
class Cli(Handler):
    PERFORMANCE_MESS = 'PERFORMANCE'
    
    COMMAND_CONJUCTION = 'conjuction'
    
    command = ''
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    args = ArgsParsed(
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

    def argparse(self):
        parser = ArgumentParser(description='Astro compute utility')
        subparsers = parser.add_subparsers(title='Subcommands', dest='command')

        subparser = subparsers.add_parser(name=self.COMMAND_CONJUCTION, description='Get planet conjuctions')
        
        time_format = str(self.TIME_FORMAT).replace('%', '')
        
        subparser.add_argument('--start', type=str, help=f"Start date: str '{time_format}' [{self.START_DEFAULT}]", required=False)
        subparser.add_argument('-e','--end', type=str, help=f"End date: str '{time_format}' [{self.END_DEFAULT}]", required=False)
        subparser.add_argument('-s','--step', type=int, help=f"Step in minutes: int [{self.STEP_MINUTES_DEFAULT}]", required=False)
        subparser.add_argument('-a','--accuracy', type=float, help=f"Degrees conjuction accuracy: float [{self.ACCURACY_DEFAULT}]", required=False)
        subparser.add_argument('--no-threads', action='store_true', help=f"Without multithreading ({self.PERFORMANCE_MESS}): bool [{self.WITH_TREADS_DEFAULT == False}]", required=False)
        subparser.add_argument('--threads-max', type=int, help=f"Threads max ({self.PERFORMANCE_MESS}): int [{self.THREAD_MAX_DEFAULT}]", required=False)
        subparser.add_argument('-p1','--planet1', type=str, help=f"Planet 1: str [SUN]", required=False)
        subparser.add_argument('-p2','--planet2', type=str, help=f"Planet 2: str [MOON]", required=False)
        args: Any = parser.parse_args()
        self.args = args
        self.command = args.command
    
        self._cast_args(args)
        

    def _cast_args(self, args: ArgsParsed):
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
