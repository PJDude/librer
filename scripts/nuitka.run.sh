#!/bin/bash

dir="$(readlink -m $(dirname "$0"))"
cd $dir/../src

VERSION=`cat ./version.txt`
VERSION=${VERSION:1:10}
echo VERSION=$VERSION

outdir=build-nuitka-lin$venvname

rm -rf ../$outdir
mkdir ../$outdir

echo running-nuitka

python3 -m nuitka --version > distro.info.txt

#--show-scons --show-progress --show-modules

#--file-reference-choice=runtime
# Nuitka-Options:INFO: Using default file reference mode 'runtime' need not be specified.

#--follow-imports
# Nuitka-Options:INFO: Following all imports is the default for onefile mode and need not be specified.

CCFLAGS='-Ofast -static' python3 -m nuitka --follow-stdlib --onefile --assume-yes-for-downloads --linux-icon=./icon.ico --include-data-file=./distro.info.txt=./distro.info.txt --include-data-file=./version.txt=./version.txt --include-data-file=./../LICENSE=./LICENSE --enable-plugin=tk-inter --output-filename=librer --output-dir=../$outdir --lto=yes ./librer.py

mv ./librer ../$outdir/librer

# --file-description='DUplicates DEtector'
# --copyright='2022-2023 Piotr Jochymek'
#--product-version=$VERSION
#--product-name='librer'
cd ../$outdir

mv ./librer ./librer-temp
mv ./librer.dist ./librer

zip -9 -r -m ./librer.nuitka.lin.zip ./librer

mv ./librer-temp ./librer
