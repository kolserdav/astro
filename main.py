from lib.conjuction import ConjuctionsParams, Conjuction
from lib.transit import TransitParams, Transit
from lib.retro import RetroParams, Retro
from lib.planet import PlanetParams, Planet
from common.cli import Cli
from datetime import timedelta


def main():

    cli = Cli()
    cli.argparse()

    if cli.command == cli.COMMAND_CONJUCTION:
        astro = Conjuction(
            timezone_str=cli.TIME_ZONE_STR_DEFAULT,
            debug=cli.DEBUG_DEFAULT
        )
        astro.show(
            ConjuctionsParams(
                start=cli.start if cli.start != None else cli.START_DEFAULT,
                end=cli.end if cli.end != None else cli.END_DEFAULT,
                step=timedelta(minutes=cli.args_conjuction.step if cli.args_conjuction.step !=
                               None else cli.STEP_MINUTES_DEFAULT),
                accuracy=cli.args_conjuction.accuracy if cli.args_conjuction.accuracy != None else cli.ACCURACY_DEFAULT,
                planet1=cli.args_conjuction.planet1 if cli.args_conjuction.planet1 != None else astro.planet.Sun,
                planet2=cli.args_conjuction.planet2 if cli.args_conjuction.planet2 != None else astro.planet.Moon,
                multiThread=False if cli.args_conjuction.no_threads == True else cli.WITH_TREADS_DEFAULT,
                maxThreads=cli.args_conjuction.threads_max if cli.args_conjuction.threads_max else cli.THREAD_MAX_DEFAULT
            )
        )
    elif cli.command == cli.COMMAND_TRANSIT:
        astro = Transit(
            timezone_str=cli.TIME_ZONE_STR_DEFAULT,
            debug=cli.DEBUG_DEFAULT
        )
        astro.show(
            TransitParams(
                start=cli.start if cli.start != None else cli.START_DEFAULT,
                end=cli.end if cli.end != None else cli.END_DEFAULT,
                step=timedelta(minutes=cli.args_transit.step if cli.args_transit.step !=
                               None else cli.STEP_MINUTES_DEFAULT),
                planet=cli.args_transit.planet if cli.args_transit.planet != None else astro.planet.Sun,
                multiThread=False if cli.args_transit.no_threads == True else cli.WITH_TREADS_DEFAULT,
                maxThreads=cli.args_transit.threads_max if cli.args_transit.threads_max else cli.THREAD_MAX_DEFAULT,
                sign=cli.args_transit.sign if cli.args_transit.sign != None else cli.SIGN_DEFAULT,
                sign_index=0,
                all=cli.args_transit.all if cli.args_transit.all != None else cli.ALL_SIGNS_DEFAULT,
                nakshatra=cli.args_transit.nakshatra if cli.args_transit.nakshatra != None else cli.NAKHATRA_DEFAULT,
                nakshatra_index=0
            )
        )
    elif cli.command == cli.COMMAND_RETRO:
        astro = Retro(
            timezone_str=cli.TIME_ZONE_STR_DEFAULT,
            debug=cli.DEBUG_DEFAULT
        )
        astro.show(
            RetroParams(
                start=cli.start if cli.start != None else cli.START_DEFAULT,
                end=cli.end if cli.end != None else cli.END_DEFAULT,
                step=timedelta(minutes=cli.args_transit.step if cli.args_transit.step !=
                               None else cli.STEP_MINUTES_DEFAULT),
                planet=cli.args_retro.planet if cli.args_retro.planet != None else astro.planet.Sun,
                multiThread=False if cli.args_retro.no_threads == True else cli.WITH_TREADS_DEFAULT,
                maxThreads=cli.args_retro.threads_max if cli.args_retro.threads_max else cli.THREAD_MAX_DEFAULT,
            )
        )
    elif cli.command == cli.COMMAND_PLANETS:
        astro = Planet(
            timezone_str=cli.TIME_ZONE_STR_DEFAULT,
            debug=cli.DEBUG_DEFAULT
        )
        astro.show(PlanetParams(
            all=cli.args_planets.all if cli.args_planets.all != None else False
        ))


main()
