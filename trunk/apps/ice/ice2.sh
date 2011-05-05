#!/bin/bash
export ICE_HOME=/Applications/Ice2/Ice2.app/Contents
export OOO_HOME=/Applications/OpenOffice.org.app/Contents
export UNO_HOME=$ICE_HOME/Resources/plugins/ooo/py25-pyuno-macosx
export URE_BOOTSTRAP=file://$OOO_HOME/program/fundamentalrc
export DYLD_LIBRARY_PATH=$UNO_HOME:$OOO_HOME/basis-link/program:$OOO_HOME/basis-link/ure-link/lib:$DYLD_LIBRARY_PATH
export PYTHONPATH=$UNO_HOME

cd /Applications/Ice2/Ice2.app/Contents/Resources
../MacOS/Ice2 "$@"
