@echo off
cd /d "%~dp0"
python -m pip install -r requirements-build.txt
python setup.py bdist_msi
