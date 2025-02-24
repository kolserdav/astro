class Retro:
    def show(self, params: RetroParams):
        self.__set_params(params)

        print(
            f"Starting, timezone: {self.timezone_str}, debug: {self.debug}, multiThreading: {self.multiThread}")

        start = datetime.now()

        retros: List[Retros] = []

        if params.multiThread:
            chunks = self.split_dates(
                start=params.start, end=params.end, step=params.step)

            with ProcessPoolExecutor() as executor:
                results = list(executor.map(
                    self.get_planet_retro,
                    [
                        RetroParams(
                            start=chunk.start,
                            end=chunk.end,
                            planet=params.planet,
                            step=params.step,
                            multiThread=params.multiThread,
                            maxThreads=params.maxThreads,
                            out=params.out
                        ) for chunk in chunks
                    ]
                ))

                retros = [
                    item for sublist in results for item in sublist]
        else:
            retros = self.get_planet_retro(RetroParams(
                start=params.start,
                end=params.end,
                planet=params.planet,
                step=params.step,
                multiThread=params.multiThread,
                maxThreads=params.maxThreads,
                out=params.out,
            ))

        print(
            f"End for: {datetime.now() - start}")
        if retros:
            print(
                f"Moments, when {params.planet} is starting or stoppind retro: {params.start}, to: {params.end}, \
for: {params.step}")
            for retro in retros:
                print(f"Time: {retro.moment.time}, Retro is: {not retro.out} Sign: {self.__show_sign(retro.sign)}, {params.planet}: {retro.sign.degrees}\
:{retro.sign.minutes}:{retro.sign.seconds}")
        else:
            print(f"There are no matches for these params: {params}")
