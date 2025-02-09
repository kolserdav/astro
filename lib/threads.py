from typing import List, Any, Callable
from threading import Thread
from queue import Queue, Empty
from dataclasses import dataclass


@dataclass
class ThreadFunc:
    func: Callable[..., Any]
    args: List[Any]


@dataclass
class Threads:
    EOF = "finished"

    queue = Queue()

    @classmethod
    def run_in_threads(cls, functions: List[ThreadFunc]):
        result: List[Any] = []
        threads: List[Thread] = []

        for func in functions:
            t = Thread(target=func.func, args=(func.args))
            threads.append(t)
            t.start()

        while True:
            try:
                message = cls.queue.get()
                if cls.EOF == message:
                    all_finished = True
                    for thread in threads:
                        if thread.is_alive():
                            all_finished = False
                            break
                    if all_finished:
                        break
                else:
                    result.append(message)
            except Empty:
                continue
        return result
