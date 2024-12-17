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

@echo|set /p="Nuitka " > distro.info.txt
python -m nuitka --version >> distro.info.txt

@echo.
@echo running-nuitka-stage_librer
python -m nuitka --windows-icon-from-ico=./icon.ico  --include-data-file=./distro.info.txt=./distro.info.txt --include-data-file=./version.txt=./version.txt --include-data-file=../LICENSE=./LICENSE --output-dir=%outdir% --standalone --lto=yes --follow-stdlib  --assume-yes-for-downloads --product-version=%VERSION% --copyright="2023-2025 Piotr Jochymek" --file-description="Librer" --enable-plugin=tk-inter --windows-disable-console --output-filename=librer ./librer.py

@echo.
@echo running-nuitka-stage_record
python -m nuitka --windows-icon-from-ico=./icon.ico  --include-data-file=./distro.info.txt=./distro.info.txt --include-data-file=./version.txt=./version.txt --include-data-file=../LICENSE=./LICENSE --output-dir=%outdir% --standalone --lto=yes --follow-stdlib  --assume-yes-for-downloads --product-version=%VERSION% --copyright="2023-2025 Piotr Jochymek" --file-description="Librer-record" ./record.py --output-filename=record

move %OUTDIR%\record.dist\record.exe %OUTDIR%\librer.dist
move %OUTDIR%\librer.dist %OUTDIR%\librer

@echo.
@echo packing
powershell Compress-Archive %OUTDIR%\librer %OUTDIR%\librer.win.zip

