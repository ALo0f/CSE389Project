# requests.py
# implements HTTP Request Processer class

from Pr0j3ct.logging import Logger

import os
import socket
import threading
import mimetypes
import urllib.parse
from email.utils import formatdate

class RequestProcessor(threading.Thread):
    def __init__(self, rootDirectory, indexFile, connSocket, connSocketAddress):
        threading.Thread.__init__(self)
        self.rootDirectory = rootDirectory
        self.indexFile = indexFile
        self.connSocket = connSocket
        self.connSocket.settimeout(1)
        self.connSocketAddress = connSocketAddress
        self.keep_alive = True
        self.logger = Logger(self.__class__.__name__+" {}".format(self.connSocketAddress))

    def run(self):
        """
        Start processing requests (called by thread scheduler)
        """
        while self.keep_alive:
            # recieve data from client socket
            try:
                received = self.connSocket.recv(2048)
            except socket.timeout: continue
            except socket.error as e:
                self.logger.error(e)
                self.stop()
                break
            # decode byte array to string (HTTP request)
            decodedMessage = received.decode("utf-8")
            # handle request
            self._handle(decodedMessage)

    def stop(self):
        """
        Stop processing requests (called by thread scheduler)
        """
        self.keep_alive = False
        self.connSocket.detach()

    def _handle(self, request):
        """
        Handle received request message (POST, GET, HEAD)
        """
        # if empty request, just skip
        if not request.strip():
            return
        # recognize message type
        type = request.split()[0].lower()
        # handle POST
        if type == "post" :
            self._handlePOST(request)
        # handle GET
        elif type == "get" :
            self._handleGET(request)
        # handle HEAD
        elif type == "head" :
            self._handleHEAD(request)
        # handle not implemented
        else:
            self._handleERROR(501, "Not Implemented")

    def _send(self, message, binary=False):
        """
        Send response to client after handling\\
        Return `True` if success\\
        Return `False` if error occured
        """
        # set timeout to blocking, for all data to be sent
        try:
            self.connSocket.settimeout(None)
            if binary:
                self.connSocket.send(message)
            else:
                self.connSocket.send(message.encode("utf-8"))
            # set back timeout
            self.connSocket.settimeout(1)
            return True
        except socket.error as e:
            self.logger.error(e)
            return False

    def _sendHEADER(self, responseCode, responseMessage, contentType, length):
        """
        send http response header
        """
        #create each line of the header
        header = [
            "HTTP/1.1 {} {}\r\n".format(responseCode, responseMessage),
            "Date: {}\r\n".format(formatdate(timeval=None, localtime=False, usegmt=True)),
            "Server: Pr0j3ct\r\n",
            "Content-Length: {}\r\n".format(length),
            "Content-Type: {}\r\n".format(contentType),
        ]
        #convert header to a single string
        header = "".join(header)
        header += "\r\n"
        #send header
        self._send(header)

    def _handleGET(self, message):
        """
        handle GET http request
        """
        # TODO: save most recent GET requests in cache (if file size is < 5MB), and reuse it when requested again
        received = message.split("\n")[0]
        targetInfo = received.split()[1]
        #convert URL to original string
        targetInfo = urllib.parse.unquote(targetInfo)
        self.logger.info("GET {}".format(targetInfo))
        #if requested root send back index file
        if targetInfo == "/" :
            with open(os.path.join(self.rootDirectory, self.indexFile), "r") as inputFile:
                data = inputFile.read()
            self._sendHEADER(200, "OK", "text/html; charset=utf-8", len(data))
            self._send(data)
        #else try to recognize target file
        else:
            # convert to relative target path
            targetInfo = "." + targetInfo
            #get abosolute filepath
            filePath = os.path.join(self.rootDirectory, targetInfo)
            # if path not exist, send 404 error
            if not os.path.exists(filePath):
                self._handleERROR(404, "File Not Found")
            # if request target is not a file, send 404 error.
            elif not os.path.isfile(filePath):
                self._handleERROR(404, "File Not Found")
            #if requested file is out of the root directory, send permission denied. 
            elif os.path.commonpath([self.rootDirectory]) != os.path.commonpath([self.rootDirectory, filePath]):
                self._handleERROR(403, "Permission Denied")
            # else send back requested file
            else:
                # get file size in bytes
                fileSize = os.path.getsize(filePath)
                # get data type
                datatype, _ = mimetypes.guess_type(filePath)
                if not datatype:
                    # if not able to guess, set to "application/octet-stream" (default binary file type)
                    datatype = "application/octet-stream"
                # send header and data
                self._sendHEADER(200, "OK", datatype, fileSize)
                with open(filePath, "rb") as inputFile:
                    while True:
                        # read every 2048 bytes
                        data = inputFile.read(2048)
                        # if no more data, stop
                        if not data: break
                        # if send data failed, break
                        if not self._send(data, binary=True): break

    def _handleHEAD(self, message):
        """
        handle HEAD http request
        """
        pass

    def _handlePOST(self, message):
        """
        handle POST http request
        """
        pass

    def _handleERROR(self, errorCode, errorMessage):
        """
        handle http request ERROR
        """
        #create each line for the response html
        body = [
            "<!DOCTYPE html>\r\n",
            "<html>\r\n",
            "<head>\r\n",
            "<title>{}</title>\r\n",
            "</head>\r\n",
            "<body>\r\n",
            "<h1>HTTP Error {}: {}</h1>\r\n"
            "</body>\r\n",
            "</html>\r\n",
        ]
        #convert body to a single string
        body = "".join(body).format(errorMessage, errorCode, errorMessage)
        #send header
        self._sendHEADER(errorCode, errorMessage, "text/html; charset=utf-8", len(body))
        #send body
        self._send(body)