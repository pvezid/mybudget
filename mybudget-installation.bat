@echo off

set "topdir=%cd%"
set "zipurl=https://github.com/pvezid/mybudget/archive/refs/heads/main.zip"
set "releasesurl=https://api.github.com/repos/pvezid/mybudget/releases/latest"
set "appdir=mybudget-main"
set "olddir=%appdir%-%Date:/=-%-%Time::=-%"
set "shortlink=%userprofile%\Desktop\mybudget.lnk"
set "runbat=%topdir%\%appdir%\mybudget-run.bat"

if not exist Scripts\activate.bat (
  echo Setting up the virtual environment
  py -m venv .
)

echo Activating the virtual environment
call Scripts\activate

if not exist version.txt (
  echo "" > version.txt
)
powershell -command "(Invoke-RestMethod -Uri '%releasesurl%').tag_name" > new_version.txt

fc /L new_version.txt version.txt > nul
if errorlevel 1 (
  if exist "%appdir%"\ (
    echo Renaming the previous application folder to "%olddir%"
    ren "%appdir%" "%olddir%"
  )

  echo Downloading the application
  curl -s -L -o "%appdir%.zip" "%zipurl%"

  echo Extracting the application
  tar -xf "%appdir%.zip"
  del "%appdir%.zip"

  del version.txt
  ren new_version.txt version.txt

  echo Installing the required modules
  cd "%appdir%"
  py -m pip install -r requirements.txt

  if exist "..\%olddir%\data\" (
    echo Copying the previous database
    xcopy "..\%olddir%\data\" "data\" /s /e
  ) else (
    if not exist data\ (
      echo Creating the initial database
      mkdir data
      py app/manage.py migrate
      py app/manage.py loaddata init
    )
  )
  del '%shortlink%'
  powershell -command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%shortlink%');$s.TargetPath='%runbat%';$s.WorkingDirectory='%topdir%\%appdir%';$s.Save()"
) else (
  del new_version.txt
)
