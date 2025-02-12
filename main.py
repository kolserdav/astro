from lib.astro import Astro, ConjuctionsParams, TransitParams
from lib.cli import Cli
from datetime import timedelta


def main():

    cli = Cli()
    cli.argparse()

    astro = Astro(
        timezone_str=cli.TIME_ZONE_STR_DEFAULT,
        debug=cli.DEBUG_DEFAULT
    )
    if cli.command == cli.COMMAND_CONJUCTION:
        astro.show_conjuctions(
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
        astro.show_transits(
            TransitParams(
                start=cli.start if cli.start != None else cli.START_DEFAULT,
                end=cli.end if cli.end != None else cli.END_DEFAULT,
                step=timedelta(minutes=cli.args_transit.step if cli.args_transit.step !=
                               None else cli.STEP_MINUTES_DEFAULT),
                planet=cli.args_transit.planet if cli.args_transit.planet != None else astro.planet.Sun,
                multiThread=False if cli.args_transit.no_threads == True else cli.WITH_TREADS_DEFAULT,
                maxThreads=cli.args_transit.threads_max if cli.args_transit.threads_max else cli.THREAD_MAX_DEFAULT,
                sign=cli.args_transit.sign if cli.args_transit.sign != None else cli.SIGN_DEFAULT,
                sign_index=0
            )
        )


main()
