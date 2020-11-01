# CSE389Project
CSE 389 Final Project

------

Test run
```cmd
python main.py website 12345
```

----
## Features:  
HTTP:  
- [X] GET 
- [ ] HEAD
- [ ] POST
- [X] ERROR Message  

Logging:  
- [X] information
- [X] warning
- [X] Error
- [ ] cacheManagement
- [ ] logFilesManagement

multi-threading:
- [x] task queue
- [x] thread status tracker
- [x] limit max threads

## Extra Feature:
- [ ] authentication
- [ ] SSL
- [ ] cache requests
- [ ] Cookie Management
- [X] support for all file types
- [X] support for large files (>1GB)

------

## HTTPS Configuration
This section shows how to generate certificate and install it for HTTPS server

### Certificate Generation
Generate SSL X509 certificate by script
```cmd
pip install pyOpenSSL
python gencert.py
```

### Certificate Installation
In order for local browser to connect HTTPS server, need to install generated certificate on local machine  

#### Windows  
Install certificate on Windows (run command in admin mode)
```cmd
python gencert.py -install
```

If no longer need certificate, delete it by  
```cmd
python gencert.py -uninstall
```
Can also manage installed certificate using `mmc`, in `certificates/Trusted Root Certification Authorities/Certificates`, find `Pr0j3ct`  

#### Linux
Install certificate on Linux
```bash
python gencert.py -install
```
To uninstall it, run
```bash
python gencert.py -uninstall
```
For `Ubuntu/Debian`, the certificate is installed at `/usr/local/share/ca-certificates/Pr0j3ct.crt`  
For `Red Hat/CentOS`, the certificate is installed at `/etc/pki/ca-trust/source/anchors/Pr0j3ct.crt`  
For `Arch Linux`, the certificate is installed at `/etc/ca-certificates/trust-source/anchors/Pr0j3ct.crt`