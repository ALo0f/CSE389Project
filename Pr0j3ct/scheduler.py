# scheduler.py
# implements Multi-thread Scheduler class

from Pr0j3ct.logging import Logger

import threading

class Scheduler:
    def __init__(self, max_threads=50):
        self.max_threads = max_threads
        self.tasks = []
        self.logger = Logger(self.__class__.__name__)

    def add(self, runnable):
        """
        Add runnable class object to thread queue
        """
        self.tasks.append(runnable)
        self._update()

    def _update(self):
        """
        Update thread pool
        1. Check for dead threads and remove them
        2. Start running new threads that are waiting
        """
        # get dead threads
        to_delete = []
        for runnable in self.tasks:
            if not runnable.keep_alive:
                to_delete.append(runnable)
        # remove dead threads
        for task in to_delete:
            self.tasks.remove(task)
        # start waiting threads, at most max_threads
        for runnable in self.tasks[:self.max_threads]:
            if not runnable.is_alive():
                runnable.start()

    def shutdown(self):
        """
        Shutdown all running threads
        """
        for runnable in self.tasks:
            if runnable.is_alive():
                runnable.stop()
                runnable.join()