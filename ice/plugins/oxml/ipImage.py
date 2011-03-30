#!/usr/bin/env ip
#    Copyright (C) 2010  Distance and e-Learning Centre,
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

import clr
clr.AddReference("System.Drawing")
import System.Drawing
from System.Drawing import Bitmap, Graphics, Rectangle
from System.Drawing.Imaging import (ImageCodecInfo, ImageFormat,
                        Encoder, EncoderParameter, EncoderParameters)
from System.Drawing.Drawing2D import InterpolationMode
HighQualityBicubic = InterpolationMode.HighQualityBicubic
from System.Diagnostics import Process
try:
    ZipFile = None
    from System.IO import MemoryStream
    clr.AddReference("Ionic.Zip.dll")
    from Ionic.Zip import ZipFile
except:
    pass


class Image(object):
    ImageEncoders = dict([(i.MimeType, i) for i in ImageCodecInfo.GetImageEncoders()])

    @staticmethod
    def ImageFromZip(zipFile, file):
        if ZipFile is None:
            raise Exception("'Ionic.Zip.dll' not found! ZipFile not supported!")
        z = ZipFile(zipFile)
        m = MemoryStream()
        e = z[file]
        e.Extract(m)
        return Image(m)

    def __init__(self, file):
        self._file = file
        self._bitmap = Bitmap(file)

    @property
    def width(self):
        return self._bitmap.Width

    @property
    def height(self):
        return self._bitmap.Height

    def resize(self, width, height):
        rImg = Bitmap(width, height)
        g = Graphics.FromImage(rImg)
        g.InterpolationMode = HighQualityBicubic
        g.DrawImage(self._bitmap, 0, 0, width, height)
        g.Dispose()
        self._bitmap.Dispose()
        self._bitmap = rImg

    def crop(self, left=0, top=0, right=0, bottom=0):
        width = self._bitmap.Width - right
        height = self._bitmap.Height - bottom
        r = Rectangle(left, top, width, height)
        try:
            cropImage = self._bitmap.Clone(r, self._bitmap.PixelFormat)
        except:
            print "retrying  rectangle=%s" % str(r)
            self.resize(self._bitmap.Width+10, self._bitmap.Height+10)
            try:
                cropImage = self._bitmap.Clone(r, self._bitmap.PixelFormat)
            except Exception, e:
                print "Error in crop: %s" % str(e)
                return
        self._bitmap.Dispose()
        self._bitmap = cropImage

    def save(self, file=None):
        if file is None:
            file = self._file
        self._bitmap.Save(file)
        self._file = file
        return True

    def saveAs(self, file):
        map = { "bmp": ImageFormat.Bmp,
                "jpg": ImageFormat.Jpeg,
                "jpeg": ImageFormat.Jpeg,
                "gif": ImageFormat.Gif,
                "exif": ImageFormat.Exif,
                "emf": ImageFormat.Emf,
                "ico": ImageFormat.Icon,
                "icon": ImageFormat.Icon,
                "png": ImageFormat.Png,
                "tif": ImageFormat.Tiff,
                "tiff": ImageFormat.Tiff,
                "wmf": ImageFormat.Wmf
                }
        try:
            ext = file.rsplit(".", 1)[1].lower()
            imageFormat = map[ext]
        except:
            raise Exception("Unknown or unsupported file ext!")
        if imageFormat==ImageFormat.Jpeg:
            return self.saveAsJpeg(file, 80)
        else:
            #print "saving as %s" % str(imageFormat)
            try:
                self._bitmap.Save(file, imageFormat)
            except Exception, e:
                print "Error saving bitmap to '%s' - '%s'" % (file, str(e))
                return False
            self._file = file
            return True


    def saveAsJpeg(self, file, quality=80): # quality ~= 10 to 100 (20 to 80)
        qualityParam = EncoderParameter(Encoder.Quality, quality)
        jpegCodec = self.ImageEncoders.get("image/jpeg")
        if jpegCodec is None:
            return False
        encoderParams = EncoderParameters(1)
        encoderParams.Param[0] = qualityParam
        self._bitmap.Save(file, jpegCodec, encoderParams)
        self._file = file
        return True

    def _display(self, file=None):
        if file is None:
            file = self._file
        p = Process.Start(file)
    def _eog(self, file=None):
        # eog - eye of gnome
        if file is None:
            file = self._file
        self._display("eog %s" % file)

    def close(self):
        if self._bitmap is not None:
            self._bitmap.Dispose()
            self._bitmap = None

    def __del__(self):
        self.close()





if __name__=="__main__":
    test()