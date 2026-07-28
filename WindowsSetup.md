# windows:
Run cmd as administrator
# classpath optional
set PYTHONHOME=c:\python-3.7.0
set PYTHONPATH=c:\python-3.7.0\Lib
set PATH=%PYTHONHOME%;%PATH%
%PYTHONHOME%;%PATH%;%PYTHONHOME%\Lib;%PYTHONHOME%\DLLs;%PYTHONHOME%\Lib\lib-tk;

#install pyenv in power shell
git clone - https://github.com/pyenv-win/pyenv-win.git "%USERPROFILE%\.pyenv"

pyenv --version

pyenv install 3.11.9 (if not install)
OR
winget install Python.Python.3.11

py --list

#Check Installed Versions
py -0
py --list

#Run a Specific Version
py -3.10
py -3.11

#venv
> py -3.11 -m venv c:\users\hp\venv311
>venv311\Scripts\activate

Unix
##python3
# python3.11 -m venv /home/mukul/venv-llm
# source /home/mukul/venv-llm/bin/activate
# deactivate

pip install pandas
