@echo off
REM Rebuild every dashboard file from scratch (run from project root, venv active)
python -m src.pipeline && python -m src.aggregate && python -m src.summarize
