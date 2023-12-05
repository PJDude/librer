#!/bin/bash

dir="$(readlink -m $(dirname "$0"))"
cd $dir/../src

VERSION=`cat ./version.txt`
VERSION=${VERSION:1:10}
echo VERSION=$VERSION

outdir=build-pyinstaller-lin$venvname

outdir_l=${outdir}_l
outdir_r=${outdir}_r

outdir_lo=${outdir}_lo
outdir_ro=${outdir}_ro

#rm -rf ../$outdir
#mkdir ../$outdir

echo ''
echo running-pyinstaller
echo wd:`pwd`

echo python:`python3 --version` > distro.info.txt
echo pyinstaller:`pyinstaller --version` >> distro.info.txt

echo ''
echo running-pyinstaller-stage1
echo wd:`pwd`

#--strip
pyinstaller --noconfirm --noconsole --clean --add-data="distro.info.txt:." --add-data="version.txt:." --add-data="../LICENSE:." --distpath=../$outdir_l ./librer.py

pyinstaller --noconfirm --console --clean --add-data="distro.info.txt:." --add-data="version.txt:." --add-data="../LICENSE:." --distpath=../$outdir_r ./record_console.py -n record

mv -v ../$outdir_r/record/record ../$outdir_l/librer

cd ../$outdir_l/
echo ''
echo running-pyinstaller-stage1-packing
echo wd:`pwd`

zip -9 -r -m ./librer.pyinstaller.lin.zip ./librer

cd ../src

echo ''
echo running-pyinstaller-stage2
echo wd:`pwd`

pyinstaller --noconfirm --noconsole --clean --add-data="distro.info.txt:." --add-data="version.txt:." --add-data="../LICENSE:." --distpath=../$outdir_lo --onefile ./librer.py

pyinstaller --noconfirm --console --clean --add-data="distro.info.txt:." --add-data="version.txt:." --add-data="../LICENSE:." --distpath=../$outdir_ro --onefile ./record_console.py -n record

