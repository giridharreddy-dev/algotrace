@echo off
cd /d "%~dp0"
where py >nul 2>&1
if errorlevel 1 goto use_python
py -3 -m unittest discover -s tests -v
goto python_done
:use_python
python -m unittest discover -s tests -v
:python_done
if errorlevel 1 goto failed
where node >nul 2>&1
if errorlevel 1 goto no_node
node --test tests/test_learning.mjs
if errorlevel 1 goto failed
echo All Python and JavaScript tests passed.
pause
exit /b 0
:no_node
echo Python tests passed. Optional JavaScript tests were not run because Node.js was not found.
pause
exit /b 0
:failed
echo Tests failed. Review the output above.
pause
exit /b 1
