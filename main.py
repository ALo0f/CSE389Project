import sys
from Pr0j3ct.server import Server


if __name__=="__main__":
    if len(sys.argv) < 3:
        print("Please run: main.py <RootDirectory> <Port>")
        sys.exit(1)
    """
    The first argument is the root directory, the second argument is the port.
    """
    root = sys.argv[1]
    port = int(sys.argv[2])
    # try to enable SSL for https
    myServer = Server(root, port, enableSSL=True)
    myServer.start()