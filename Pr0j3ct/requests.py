# requests.py
# implements HTTP Request Processer class

from Pr0j3ct.logging import Logger

class RequestProcessor:
    def __init__(self, rootDirectory, indexFile, connSocket):
        pass

    def run(self):
        """
        Start processing requests (called by thread scheduler)
        """
        pass

    def stop(self):
        """
        Stop processing requests (called by thread scheduler)
        """
        pass

    def handle(self, request):
        """
        Handle received request message (POST, GET, HEAD)
        """
        pass

    def send(self, message):
        """
        Send response to client after handling
        """
        pass