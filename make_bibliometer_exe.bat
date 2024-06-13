:: Bertin F. 26-05-2024

@echo off
Title Create BiblioMeter exe

:: set useful dir
set working_dir=%TEMP%/BIBLIO_exe
set save_dir=%userprofile%/Desktop

mkdir %working_dir%
@echo Create %working_dir% successfully

:: create a venv with python 3.9.7
:: adapted from https://stackoverflow.com/questions/45833736/how-to-store-python-version-in-a-variable-inside-bat-file-in-an-easy-way?noredirect=1
cd %working_dir%
%userprofile%/PyVersions/python3.9.7/python -m venv venv
for /F "tokens=* USEBACKQ" %%F in (`python --version`) do (set var=%%F)
echo Create a virtual environment with %var%
::python -m venv venv


:: activate the venv
set VIRTUAL_ENV=%working_dir%\venv
if defined _OLD_VIRTUAL_PYTHONHOME set PYTHONHOME=%_OLD_VIRTUAL_PYTHONHOME%
if defined PYTHONHOME set _OLD_VIRTUAL_PYTHONHOME=%PYTHONHOME%
set PYTHONHOME=
if defined _OLD_VIRTUAL_PATH set PATH=%_OLD_VIRTUAL_PATH%
if not defined _OLD_VIRTUAL_PATH set _OLD_VIRTUAL_PATH=%PATH%
set PATH=%VIRTUAL_ENV%/Scripts;%PATH%

:: builds the BIBLIO_Meter python program

set "PGM=%working_dir%/App.py "
echo from BiblioMeter_GUI.Page_Classes import app_main > %PGM%
echo app = app_main() >> %PGM%
echo app.mainloop() >> %PGM%

:: install packages

pip install git+https://github.com/TickyWill/BiblioParsing.git#egg=BiblioParsing
pip install git+https://github.com/TickyWill/BiblioMeter.git#egg=BiblioMeter
pip install auto-py-to-exe

:: set the default directories
:: PGM contain the application launch python program

set "FUNC=%working_dir%/venv/Lib/site-packages/BiblioMeter_FUNCTS;BiblioMeter_FUNCTS/"
set "GUI=%working_dir%/venv/Lib/site-packages/BiblioMeter_GUI;BiblioMeter_GUI/"
set "PARSE=%working_dir%/venv/Lib/site-packages/BiblioParsing;BiblioParsing/"

:: make the executable App.exe located is dist

pyinstaller --noconfirm --onefile --console^
 --add-data "%FUNC%"^
 --add-data "%GUI%"^
 --add-data "%PARSE%"^
 "%PGM%"

:: rename the directory dist to aaaa_mm_jj BiblioMeter 
:: adapted from http://stackoverflow.com/a/10945887/1810071
for /f "skip=1" %%x in ('wmic os get localdatetime') do if not defined MyDate set MyDate=%%x
for /f %%x in ('wmic path win32_localtime get /format:list ^| findstr "="') do set %%x
set fmonth=00%Month%
set fday=00%Day%
set dirname="%Year%-%fmonth:~-2%-%fday:~-2% BiblioMeter"
rename dist %dirname%

:: cleaning
:: remote the directories build and dist
:: set the directories build and dist used when making the executable

set "BUILD=%working_dir%\build"
rmdir /s /q %BUILD%
del App.spec

set "new_file_name=%dirname%.exe"
ren %working_dir%/%dirname%/App.exe %new_file_name%
echo %new_file_name% is located in %working_dir%\%dirname%

:: Copy Exe
set "new_file_name=%dirname%.exe"
ren %working_dir%/%dirname%/BIBLIO_METER.exe %new_file_name%
echo %new_file_name% is located in %working_dir%/%dirname% 

:: Copy Exe
set input_file=%working_dir%/%dirname%/%dirname%.exe%
set /p "rep=Do you want to copy this file in an other folder (y/n): "
if NOT %rep%==y GOTO FIN
set /p "rep1=Do you want to use %save_dir% (y/n): "
if NOT %rep%==y GOTO A
copy  %input_file% %save_dir%
GOTO FIN
A: set /p "new_dir=Enter the full path of the folder: "
set output_file=%new_dir%/%dirname%.exe%
copy  %input_file% %output_file%
:FIN

pause
