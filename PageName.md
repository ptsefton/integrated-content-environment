#Installing ICE Service in Ubuntu

This page describes the installation steps in setting up ICE Service for Ubuntu.

# Tested #
  * Ubuntu 9.04 (Jaunty Jackalope)
  * Ubuntu 9.10 (Karmic Koala), 3rd March 2010

# Documentation #
### ICE Service Installation ###
NOTE: If you do not have a previous installation of ICE either as a program or a server, you must install the required modules for ICE. Follow the installation instructions below:

#### Install subversion ####
Subversion can be installed through Synaptic Package manager or sudo aptitude install command:
```
sudo apt-get install subversion 
```

#### Install Daemon package ####
```
sudo apt-get install daemon
```

#### Install python libraries ####
  1. Add the following via Synaptic Package manager or sudo aptitude install command:
```
sudo apt-get install python-gdata python-svn python-libxslt1 python-paste python-twisted python2.6-dev python-cheetah python-textile python-openid python-lxml python-pycurl python-pypdf python-reportlab build-essential python-setuptools idle
```

> 3. The Python packages can be verified by:
```
python
import Image
import libxslt
import libxml2
import pysvn
import Cheetah
import paste
import rdflib
import gdata
import textile
import openid
import lxml
import pycurl
import pyPdf
import reportlab
import foresite
```

Checkout ICE


### Available Services for ICE Server ###
'''Services & Required libraries''':
  * [wiki:ICEService/WriterWord OpenOffice.org Writer document (.odt) and Ms Office Word document (.doc) conversion service]
  * [wiki:ICEService/SpreadsheetExcel OpenOffice.org Spreadsheet document (.ods) and Ms Office Excel document (.xls) conversion service]
  * [wiki:ICEService/PresentationPowerPoint OpenOffice.org Presentation document (.odp) and Ms Office PowerPoint document (.ppt) conversion service]
  * [wiki:ICEService/SVG Scalable Vector Graphics (.svg) conversion service]
  * [wiki:ICEService/GeoGebra GeoGebra (.ggb) conversion service]
  * [wiki:ICEService/LaTeX LaTeX (.tex) conversion service]
  * [wiki:ICEService/Wave Wave (.wav, .aiff) to MP3 (.mp3) conversion service]
  * [wiki:ICEService/CML Chemical Markup Language (.cml) conversion service]
  * [wiki:ICEService/AudioVideo Audio/video (.mp3, .m4a, .mp4, .wav, .wma) to Flash video file (.flv) conversion service]
  * [wiki:ICEService/TextToSpeech Text (.txt) to Speech conversion service]
  * [wiki:ICEService/ResizeImage Resizing images (.png, .jpg, .jpeg, .gif, .bmp) conversion service]
  * [wiki:ICEService/PdfToHtml Pdf to Html (.pdf) conversion service]

### Configuration file for ICE Server ###
  * Required variables to setup ICE Server
| '''Variable name''' | '''Variable type''' | '''Variable value''' |
|:--------------------|:--------------------|:---------------------|
| iceWebPort          |                     | specify the port number (by default is 8000) |
| host                | string              | "localhost" or you can put your server IP address |
| asServiceOnly       | boolean             | "True"               |
| enableExternalAccess | boolean             | "True"               |
| webServer           | string              | "Paste"              |

  * Save http://ice.usq.edu.au/svn/ice/trunk/apps/ice/config_sample.xml as config.xml in ~/ice-source/ice
  * Open the config.xml file using vi or gedit, and modify the following value:
```
<var name="host" type="string" value="[server IP address or localhost]"/>
<var name="asServiceOnly" type="boolean" value="True"/>
<var name="enableExternalAccess" type="boolean" value="True"/>
```

> Add another variable for webServer in the config.xml after the "enableExternalAccess" variable
```
<var name="webServer" type="string" value="Paste"/>
```

### OpenOffice 3.0 ###
OpenOffice 3.0 is pre-installed with Ubuntu 9.04. If not however,
```
sudo apt-get install openoffice.org
```

### Running ICE as server ###
'''Run OpenOffice from your terminal''': [[BR](BR.md)]
Create a script called ooo-start.sh in your home directory with the following contents:
```
#!/bin/sh
sudo soffice "-accept=socket,host=localhost,port=2002;urp;" -headless
```

'''Run ICE''':

[ICE\_Installation\_path](ICE_Installation_path.md) is the directory where ICE located. e.g. ~/ice-source

Create a script called ice-start.sh in your home directory with the following contents:
```
#!/bin/sh
sudo -E daemon -i --name=ice --chdir=[ICE_Installation_path]/ice --command=python ice2.py
```

'''Run the service from browser''':

[host](host.md) and [iceWebPort](iceWebPort.md) values are based on the values that is set in the above config.xml file. e.g. http://localhost:8000/api/convert/
```
http://[host]:[iceWebPort]/api/convert/
```

'''Stop ICE''':

Create a script called ice-stop.sh in your home directory with the following contents:
```
#!/bin/sh
sudo -E daemon -i --name=ice --stop
```