#!/bin/sh
rm -rf dist
export VERSIONER_PYTHON_PREFER_32_BIT=yes
python setup.py py2app --no-strip
rm ice.py
rm -rf  build
rm -rf ../../bin/macosx/Ice2.app

cp version_info.txt dist/Ice2.app/Contents/Resources
mkdir -p dist/Ice/setup
cp ../../templates/Configure-OOo.ott "dist/Ice/setup/Configure OpenOffice.org.odt"
cp macosx/*.webloc dist/Ice/setup

cp -R dist/Ice2.app  ../../bin/macosx 
mv dist/Ice2.app dist/Ice
rm "../../../downloads/latest/binaries/macosx/ice$1.dmg"

mv dist/Ice dist/Ice_img
mkdir "dist/Ice$1"
mv dist/Ice_img "dist/Ice$1/Ice2"
hdiutil create -srcfolder "dist/Ice$1" "../../../downloads/latest/binaries/macosx/ice$1.dmg"

