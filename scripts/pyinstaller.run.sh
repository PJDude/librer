#!/bin/bash

dir="$(readlink -m $(dirname "$0"))"
cd $dir/../src

VERSION=`cat ./version.txt`
VERSION=${VERSION:1:10}
echo VERSION=$VERSION

outdir=../build-pyinstaller$venvname

rm -rf $outdir
mkdir $outdir

echo ''
echo running-pyinstaller
echo wd:`pwd`

echo `python3 --version` > distro.info.txt
echo pyinstaller `pyinstaller --version` >> distro.info.txt

echo ''
echo running-pyinstaller-stage_librer
pyinstaller --strip --noconfirm --noconsole --clean --add-data="distro.info.txt:." --add-data="version.txt:." --add-data="../LICENSE:." --contents-directory=internal --distpath=$outdir --additional-hooks-dir=. --collect-binaries tkinterdnd2 --optimize 2 ./librer.py

echo ''
echo running-pyinstaller-stage_record
pyinstaller --strip --noconfirm --console --clean --add-data="distro.info.txt:." --add-data="version.txt:." --add-data="../LICENSE:." --contents-directory=internal --distpath=$outdir --optimize 2 ./record.py -n record

mv -v $outdir/record/record $outdir/librer

echo ''
echo packing
cd $outdir
zip -9 -r -m ./librer.lin.zip ./librer

