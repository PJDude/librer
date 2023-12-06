@cd "%~dp0.."
@echo building with pyinstaller
@cd src

@set /p VERSION=<version.txt
@SET VERSION=%VERSION:~1,10%
@echo VERSION=%VERSION%

SET OUTDIR=..\build-pyinstaller%VENVNAME%

@rmdir /s /q %OUTDIR%
@mkdir %OUTDIR%

pyinstaller --noconfirm --clean --add-data="version.txt;." --add-data="../LICENSE;." --icon=icon.ico --distpath=%OUTDIR% --windowed --contents-directory=internal librer.py  || exit /b 2
pyinstaller --noconfirm --clean --add-data="version.txt;." --add-data="../LICENSE;." --icon=icon.ico --distpath=%OUTDIR% --console --hide-console hide-early --contents-directory=internal record.py  || exit /b 1

move %OUTDIR%\record\record.exe %OUTDIR%\librer

powershell Compress-Archive %OUTDIR%\librer %OUTDIR%\librer.win.zip

exit

