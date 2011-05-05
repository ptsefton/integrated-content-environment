#!/bin/sh
OSNAME=`uname`
OSVER=`uname -r`
if [ "$OSNAME" = "Darwin" ]; then
    cd `dirname $0` &> /dev/null
    ICE_HOME=`pwd`
    if [ "$OSVER" = "10.4.0" ]; then
        UNO_HOME="$ICE_HOME/plugins/ooo/py26-pyuno-macosx"
    else
        UNO_HOME="$ICE_HOME/plugins/ooo/py25-pyuno-macosx"
    fi
    OOO_HOME="/Applications/OpenOffice.org.app/Contents"
    if [ -f "$OOO_HOME/program/fundamentalrc" ]; then
        export URE_BOOTSTRAP="vnd.sun.star.pathname:$OOO_HOME/program/fundamentalrc" 
        export DYLD_LIBRARY_PATH="/usr/lib:$UNO_HOME:$OOO_HOME/basis-link/ure-link/lib:$DYLD_LIBRARY_PATH"
    fi
    export VERSIONER_PYTHON_PREFER_32_BIT=yes
fi
export PYTHONPATH=$UNO_HOME
python ice2.py "$@"
#python
