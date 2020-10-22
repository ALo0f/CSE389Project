import os
import sys
from Pr0j3ct.server import Server

if __name__=="__main__":
    if len(sys.argv) < 3:
        print("Please run: main.py <RootDirectory> <Port>")
        sys.exit(1)
    root = sys.argv[1]
    port = int(sys.argv[2])
    myServer = Server(root, port)
    myServer.start()