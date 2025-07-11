@cd "%~dp0.."
@echo building with pyinstaller
@cd src

@set /p VERSION=<version.txt
@SET VERSION=%VERSION:~1,10%
@echo VERSION=%VERSION%

@SET OUTDIR=..\build-pyinstaller

@if exist %OUTDIR% rmdir /s /q %OUTDIR%
@mkdir %OUTDIR%

@echo.
@echo running-pyinstaller
@echo wd:%CD%

@python --version > distro.info.txt
@echo|set /p="pyinstaller " >> distro.info.txt
@pyinstaller --version >> distro.info.txt

@echo.
@echo running-pyinstaller-stage_librer
pyinstaller --version-file=version.pi.librer.txt --noconfirm --clean --add-data="distro.info.txt:." --add-data="version.txt;." --add-data="../LICENSE;." --icon=icon.ico --distpath=%OUTDIR% --windowed --contents-directory=internal --additional-hooks-dir=. --collect-binaries tkinterdnd2 --collect-data dateparser --optimize 2 librer.py  || exit /b 2

@echo.
@echo running-pyinstaller-stage_record
pyinstaller --version-file=version.pi.record.txt --noconfirm --clean --add-data="distro.info.txt:." --add-data="version.txt;." --add-data="../LICENSE;." --icon=icon.ico --distpath=%OUTDIR% --console --hide-console hide-early --contents-directory=internal --optimize 2 record.py  || exit /b 1

move %OUTDIR%\record\record.exe %OUTDIR%\librer

@echo.
@echo packing
powershell Compress-Archive %OUTDIR%\librer %OUTDIR%\librer.win.zip

