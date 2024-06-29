:: Creation: F. Bertin 2024-05-26
:: Refactoring: A. Chabli 2024-06-17

@echo off 
Title BiblioMeter.exe making

:: Setting useful editing parameters
set "TAB=   "

:: Setting useful directories
set "working_dir=%TEMP%\BIBLIO_exe"
set "save_dir=%userprofile%\Desktop"

:: Setting the name of the log file to debbug the executable making
set "LOG=%working_dir%\log.txt"

:: Creating a clean %working_dir%
echo Creating a clean %working_dir%
if exist %working_dir% (
    echo %TAB%%working_dir% exists and will be removed - Please wait
    rmdir /s /q %working_dir%
    if not exist %working_dir% (
        echo %TAB%Existing %working_dir% removed
        ) else (
            echo %TAB%Unable to remove existing %working_dir%
            GOTO FIN
            ))
mkdir %working_dir%
if exist %working_dir% (
    echo ******* REPORT ON BiblioMeter EXECUTABLE MAKING ******* > %LOG%
    echo %working_dir% successfully created >> %LOG% 
    echo %TAB%%working_dir% successfully created
    echo:
) else (
    echo %TAB%Unable to create %working_dir%
    GOTO FIN)

:: Creating a venv
:: adapted from https://stackoverflow.com/questions/45833736/how-to-store-python-version-in-a-variable-inside-bat-file-in-an-easy-way?noredirect=1
echo Creating a virtual environment
cd %working_dir%
set "python_dir=%userprofile%\PyVersions\python3.9.7"
if exist %python_dir% ( 
    echo %TAB%%python_dir% will be used to build the venv
    echo:
    %python_dir%\python -m venv venv
) else (
    echo %TAB%Unable to access %python_dir% so we will use the default python version
    echo:
    python -m venv venv)
    
:: Upgrading pip version
echo Upgrading pip version
venv\Scripts\python.exe -m pip install --upgrade pip
echo %TAB%Upgraded pip to latest version
echo:

:: Activating the venv
echo Activating the virtual environment
set "virtual_env=%working_dir%\venv"
if defined _old_virtual_pythonhome set pythonhome=%_old_virtual_pythonhome%
if defined pythonhome set _old_virtual_pythonhome=%pythonhome%
set pythonhome=
if defined _old_virtual_path set PATH=%_old_virtual_path%
if not defined _old_virtual_path set _old_virtual_path=%PATH%
set "PATH=%virtual_env%\Scripts;%PATH%"

:: Getting and displaying the python version used
for /F "tokens=* USEBACKQ" %%F in (`python --version`) do (set var=%%F)
if exist %working_dir%\venv (
    echo A virtual environment created with %var% and activated >> %LOG%
    echo %TAB%A virtual environment created with %var% and activated
    echo:
) else (
    echo Unable to create a virtual environment >> %LOG%
    echo %TAB%Unable to create a virtual environment
    GOTO FIN)

:: Installing packages
echo Installing BiblioParsing package
echo:
pip install git+https://github.com/TickyWill/BiblioParsing.git#egg=BiblioParsing
cls
echo The package BiblioParsing successfully installed >> %LOG%
echo:
echo The package BiblioParsing successfully installed
echo:
echo Installing BiblioMeter packages
echo:
pip install git+https://github.com/TickyWill/BiblioMeter.git#egg=BiblioMeter
cls
echo The package BiblioMeter successfully installed >> %LOG%
echo:
echo The BiblioMeter packages successfully installed
echo:
echo Installing auto-py-to-exe packages
echo:
pip install auto-py-to-exe
cls
echo The package auto-py-to-exe successfully installed >> %LOG%
echo:
echo The package auto-py-to-exe successfully installed
echo:    

:: Getting the python program to launch the application
echo Getting the python program to launch the application
set "PGM=%working_dir%\venv\Lib\site-packages\bmfuncts\ConfigFiles\App.py"
if exist %PGM% (
    echo The python program %PGM% successfully found >> %LOG%
    echo %TAB%The python program %PGM% successfully found
    echo:         
) else ( 
    echo Unable to get the python program %PGM% >> %LOG%
    echo %TAB%Unable to get the python program %PGM%
    GOTO FIN)

:: Setting the icon and the directories to add
set "ICON=%working_dir%/venv/Lib/site-packages/bmfuncts/ConfigFiles/BM-logo.ico"
set "FUNC=%working_dir%/venv/Lib/site-packages/bmfuncts;bmfuncts/"
set "GUI=%working_dir%/venv/Lib/site-packages/bmgui;bmgui/"
set "PARSE=%working_dir%/venv/Lib/site-packages/BiblioParsing;BiblioParsing/"

:: Making the executable App.exe to be located in dist
cls
echo Making the executable App.exe to be located in dist
echo:
pyinstaller --noconfirm --onefile --console^
 --icon="%ICON%"^
 --add-data "%FUNC%"^
 --add-data "%GUI%"^
 --add-data "%PARSE%"^
 "%PGM%"
if exist %working_dir%\dist\App.exe (
    echo The executable App.exe successfully made in dist directory >> %LOG%
    echo:
    echo %TAB%The executable App.exe successfully made in dist directory
    cls
) else (
    echo Making of the executable App.exe failed >> %LOG%
    echo:
    echo %TAB%Making of the executable App.exe failed
    GOTO FIN)

:: Renaming the directory dist to aaaa_mm_jj BiblioMeter 
:: adapted from http://stackoverflow.com/a/10945887/1810071
echo Renaming the directory dist
for /f "skip=1" %%x in ('wmic os get localdatetime') do if not defined MyDate set MyDate=%%x
for /f %%x in ('wmic path win32_localtime get /format:list ^| findstr "="') do set %%x
set fmonth=00%Month%
set fday=00%Day%
set dirname="%Year%-%fmonth:~-2%-%fday:~-2% BiblioMeter"
rename %working_dir%\dist %dirname%
if not exist %working_dir%\dist (
    echo The executable directory successfully renamed to %dirname% >> %LOG%
    echo %TAB%The executable directory successfully renamed to %dirname%
    echo:
) else (
    echo The executable directory renaming failed >> %LOG%
    echo %TAB%The executable directory renaming failed
    GOTO FIN)

:: Cleaning the working dir
:: Removing delating the directories and the files used only for making the executable (except venv)
echo Cleaning the working dir
rmdir /s /q %working_dir%\build
if not exist %working_dir%\build (echo %TAB%%TAB%build dir successfully removed)
del /f %working_dir%\App.py
if not exist %working_dir%\App.py (echo %TAB%%TAB%App.py file successfully delated)
if exist %working_dir%\App.spec (del /f %working_dir%\App.spec)
if not exist %working_dir%\App.spec (echo %TAB%%TAB%App.spec file successfully delated)
echo %working_dir% cleaned successfully >> %LOG%
echo %TAB%%working_dir% cleaned successfully 
echo:

:: Renaming the built exe
echo Renaming the built exe
set "new_file_name=%dirname%.exe"
ren %dirname%\App.exe %new_file_name%
if exist %dirname%\%new_file_name% (
    echo The executable is renamed to %new_file_name% >> %LOG%
    echo The executable is located in the directory: %working_dir%\%dirname% >> %LOG%
    echo %TAB%The executable is renamed to %new_file_name%    
    echo %TAB%The executable is located in the directory:
    echo %TAB%%TAB%%working_dir%\%dirname%
) else (
    echo The executable still named App.exe >> %LOG%
    echo The executable is located in %working_dir%\%dirname% >> %LOG%
    echo %TAB%The executable still named App.exe and is located in the directory:
    echo %TAB%%TAB%%working_dir%\%dirname%)

:: Copying the built exe to a user folder
echo:
echo Copying the built exe to a user folder
set "input_file=%working_dir%\%dirname%\%new_file_name%"
set /p "rep=Do you want to copy this file in an other folder (y/n): "
if NOT %rep%==y GOTO FIN
set /p "rep=Do you want to use %save_dir% (y/n): "
if NOT %rep%==y GOTO A
copy  %input_file% %save_dir%
echo %new_file_name% saved in %save_dir% >> %LOG%
echo %TAB%%new_file_name% saved in %save_dir%
echo:
GOTO FIN
A: set /p "new_dir=Enter the full path of the folder: "
set "output_file=%new_dir%\%new_file_name%"
copy  %input_file% %output_file%
echo %new_file_name% saved in %output_file% >> %LOG%
echo %TAB%%new_file_name% saved in %output_file%
:FIN
echo:
echo The report on the executable making is available in the file:
echo %TAB%%LOG%
echo:

pause
