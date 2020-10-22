# scheduler.py
# implements Multi-thread Scheduler class

from Pr0j3ct.logging import Logger

class Scheduler:
    def __init__(self, max_threads=50):
        self.max_threads = max_threads

    def add(self, runnable):
        """
        Add runnable class object to thread queue
        """
        pass

    def shutdown(self):
        """
        Shutdown all running threads
        """
        pass