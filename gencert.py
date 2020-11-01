# This file creates a X509 certificate for HTTPS support
# reference: https://stackoverflow.com/questions/27164354/create-a-self-signed-x509-certificate-in-python

import os
import sys
import socket
from OpenSSL import crypto

FILE_FOLDER = "certificates"
FILE_CRT = "signed.crt"
FILE_KEY = "signed.private.key"

def generate_certificate():
    if not os.path.exists(FILE_FOLDER):
        os.makedirs(FILE_FOLDER)
    if (not os.path.isfile(os.path.join(FILE_FOLDER, FILE_CRT))) or \
       (not os.path.isfile(os.path.join(FILE_FOLDER, FILE_KEY))):
        # generate a new pair
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)
        # create and fill a X509 certificate
        cert = crypto.X509()
        cert.get_subject().C = "US"                     # country
        cert.get_subject().ST = "New York"              # state/province
        cert.get_subject().L = "Syracuse"               # locality
        cert.get_subject().O = "CSE389 Pr0j3ct Team"    # orgnization
        cert.get_subject().OU = "CSE389 Team"           # orgnization unit
        cert.get_subject().CN = "Pr0j3ct"               # common name
        cert.set_serial_number(2077)                    # serial number
        cert.set_version(2)                             # version
        cert.add_extensions([
            crypto.X509Extension(b'subjectAltName', False,
                ",".join([
                    "DNS:{}".format(socket.gethostname()),
                    "DNS:*.{}".format(socket.gethostname()),
                    "DNS:localhost",
                    "DNS:*.localhost"
                ]).encode()),
            crypto.X509Extension(b"basicConstraints", True, b"CA:true")
        ])                                              # set extensions
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10*365*24*60*60)       # expiration time in seconds
        cert.set_issuer(cert.get_subject())             # issuer
        cert.set_pubkey(key)                            # public key
        cert.sign(key, "SHA256")                        # sign
        # save files
        with open(os.path.join(FILE_FOLDER, FILE_CRT), "wb") as certFile:
            certFile.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        with open(os.path.join(FILE_FOLDER, FILE_KEY), "wb") as keyFile:
            keyFile.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
        print("certificate generated successfully")
    else:
        print("certificate file already exists")

def install_certificate():
    # if windows
    if os.name == "nt":
        os.system("certutil -addstore root {}".format(os.path.join(FILE_FOLDER, FILE_CRT)))
    # if linux
    elif os.name == "posix":
        from shutil import which
        # check for update-ca-certificates
        if which("update-ca-certificates") is not None:
            # ubuntu / debian
            path = os.path.join("/", "usr", "local", "share", "ca-certificates")
            if not os.path.exists(path):
                raise Exception("{} path not found, action failed".format(path))
            os.system("sudo cp {} {}".format(os.path.join(FILE_FOLDER, FILE_CRT), os.path.join(path, "Pr0j3ct.crt")))
            os.system("sudo update-ca-certificates")
        elif which("update-ca-trust") is not None:
            path1 = os.path.join("/", "etc", "pki", "ca-trust", "source", "anchors")
            path2 = os.path.join("/", "etc", "ca-certificates", "trust-source", "anchors")
            if os.path.exists(path1):
                # red hat / centos
                os.system("sudo update-ca-trust force-enable")
                os.system("sudo cp {} {}".format(os.path.join(FILE_FOLDER, FILE_CRT), os.path.join(path1, "Pr0j3ct.crt")))
                os.system("sudo update-ca-trust extract")
            elif os.path.exists(path2):
                # arch
                os.system("sudo cp {} {}".format(os.path.join(FILE_FOLDER, FILE_CRT), os.path.join(path2, "Pr0j3ct.crt")))
                os.system("sudo update-ca-trust")
            else:
                raise Exception("Platform not supported, action failed")
        else:
            raise Exception("Platform not supported, action failed")
        print("Certificate installed successfully")
    # otherwise, not supported
    else:
        raise Exception("{} platform is not supported".format(os.name))

def uninstall_certificate():
    # if windows
    if os.name == "nt":
        os.system("certutil -delstore root \"Pr0j3ct\"")
    # if linux
    elif os.name == "posix":
        from shutil import which
        # check for update-ca-certificates
        if which("update-ca-certificates") is not None:
            # ubuntu / debian
            path = os.path.join("/", "usr", "local", "share", "ca-certificates")
            if not os.path.exists(path):
                raise Exception("{} path not found, action failed".format(path))
            os.system("sudo rm -f {}".format(os.path.join(path, "Pr0j3ct.crt")))
            os.system("sudo update-ca-certificates --fresh")
        elif which("update-ca-trust") is not None:
            path1 = os.path.join("/", "etc", "pki", "ca-trust", "source", "anchors")
            path2 = os.path.join("/", "etc", "ca-certificates", "trust-source", "anchors")
            if os.path.exists(path1):
                # red hat / centos
                os.system("sudo rm -f {}".format(os.path.join(path1, "Pr0j3ct.crt")))
                os.system("sudo update-ca-trust extract")
            elif os.path.exists(path2):
                # arch
                os.system("sudo rm -f {}".format(os.path.join(path2, "Pr0j3ct.crt")))
                os.system("sudo update-ca-trust")
            else:
                raise Exception("Platform not supported, action failed")
        else:
            raise Exception("Platform not supported, action failed")
        print("Certificate unintalled successfully")
    # otherwise, not supported
    else:
        raise Exception("{} platform is not supported".format(os.name))

if __name__=="__main__":
    generate_certificate()
    if len(sys.argv) >= 2:
        if sys.argv[1] == "-install":
            install_certificate()
        elif sys.argv[1] == "-uninstall":
            uninstall_certificate()
        else:
            print("Only support argument \"-install\" or \"-uninstall\"")