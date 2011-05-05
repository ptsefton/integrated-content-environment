#
#    Copyright (C) 2008  Distance and e-Learning Centre, 
#    University of Southern Queensland
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from system import System

system = System()

rsvg_options = ["dpi-x", "dpi-y", "x-zoom", "y-zoom", "zoom", "width", "height",
                "format", "output", "keep-aspect-ratio", "version", "base-uri"]

def rsvg_available():
    stdout, _ = system.execute2("rsvg-convert", "--version")
    return stdout.startswith("rsvg-convert")

def rsvg_convert(filename, *args):
    if filename is not None:
        _, stdout, stderr = system.execute3("rsvg-convert", filename, *args)
        out = stdout.read()
        err = stderr.read()
        stdout.close()
        stderr.close()
        if len(err) > 0 and err.find("WARNING") == -1:
            raise Exception(err + out)
        return out
    else:
        raise Exception("Error: No SVG file specified")
    