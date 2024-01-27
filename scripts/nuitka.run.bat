@cd "%~dp0.."
@echo building with nuitka
@cd src

@set /p VERSION=<version.txt
@SET VERSION=%VERSION:~1,10%
@echo VERSION=%VERSION%

@SET OUTDIR=..\build-nuitka

@if exist %OUTDIR% rmdir /s /q %OUTDIR%
@mkdir %OUTDIR%

@echo.
@echo running-nuitka
@echo wd:%CD%

@echo|set /p="nuitka " > distro.info.txt
python -m nuitka --version >> distro.info.txt

@echo.
@echo running-nuitka-stage_librer
python -m nuitka --include-data-file=./distro.info.txt=./distro.info.txt --include-data-file=./version.txt=./version.txt --include-data-file=../LICENSE=./LICENSE --enable-plugin=tk-inter --lto=yes --follow-stdlib  --assume-yes-for-downloads --windows-disable-console --output-dir=%outdir% --standalone --output-filename=librer ./librer.py

@echo.
@echo running-nuitka-stage_record
python -m nuitka --include-data-file=./distro.info.txt=./distro.info.txt --include-data-file=./version.txt=./version.txt --include-data-file=../LICENSE=./LICENSE --output-dir=%outdir% --lto=yes --follow-stdlib  --assume-yes-for-downloads --standalone ./record.py --output-filename=record

move %OUTDIR%\record.dist\record.exe %OUTDIR%\librer.dist
move %OUTDIR%\librer.dist %OUTDIR%\librer

@echo.
@echo packing
powershell Compress-Archive %OUTDIR%\librer %OUTDIR%\librer.win.zip

