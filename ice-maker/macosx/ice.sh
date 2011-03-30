#!/bin/sh
cd `dirname $0` &> /dev/null
MACOS_HOME=`pwd`
cd $MACOS_HOME/../Resources &> /dev/null
ICE_HOME=`pwd`
OSNAME=`uname`
if [ "$OSNAME" = "Darwin" ]; then
    UNO_HOME="$ICE_HOME/plugins/ooo/py25-pyuno-macosx"
    OOO_HOME="/Applications/OpenOffice.org.app/Contents"
    if [ -f "$OOO_HOME/program/fundamentalrc" ]; then
        export URE_BOOTSTRAP="vnd.sun.star.pathname:$OOO_HOME/program/fundamentalrc"
        export DYLD_LIBRARY_PATH="$UNO_HOME:$OOO_HOME/basis-link/program:$OOO_HOME/basis-link/ure-link/lib:$DYLD_LIBRARY_PATH"
    fi
    export PYTHONPATH=$ICE_HOME/lib/python2.5
fi
$MACOS_HOME/Ice2.bin $*
