PY=python

.PHONY: install install-dev format lint gui sem sim

install:
	$(PY) -m pip install -r requirements.txt

install-dev:
	$(PY) -m pip install -r requirements-dev.txt

format:
	black source
	isort source

lint:
	ruff check .

gui:
	$(PY) source/images_to_video_gui.py

sem:
	$(PY) source/sem-analysis.py

sim:
	$(PY) source/auto_run_simulation.py
