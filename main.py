from lib.astro import Astro, ConjuctionsParams
from lib.cli import Cli
from datetime import datetime, timedelta

def main():

    cli = Cli()
    cli.argparse()     
    if cli.command == cli.COMMAND_CONJUCTION: 
        astro = Astro(timezone_str=cli.TIME_ZONE_STR_DEFAULT)
        astro.show_conjuctions(
            ConjuctionsParams(
                start=cli.start if cli.start != None else cli.START_DEFAULT,
                end=cli.end if cli.end != None else cli.END_DEFAULT,
                step=timedelta(minutes=cli.args.step if cli.args.step != None else cli.STEP_MINUTES_DEFAULT),
                accuracy=cli.args.accuracy if cli.args.accuracy != None else cli.ACCURACY_DEFAULT,
                planet1=cli.args.planet1 if cli.args.planet1 != None else astro.planet.Sun,
                planet2=cli.args.planet2 if cli.args.planet2 != None else astro.planet.Moon,
                multiThread=False if cli.args.no_threads == True else cli.WITH_TREADS_DEFAULT,
                debug=cli.DEBUG_DEFAULT,
                maxThreads=cli.args.threads_max if cli.args.threads_max else cli.THREAD_MAX_DEFAULT   
            )
    )
main()
    
