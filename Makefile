.PHONY: run install lint format clean test

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
TEST_MODE := "on"

# Helper function to activate or create and activate the virtual environment
define ensure_venv
	@if [ ! -d "$(VENV)" ]; then \
		python3 -m venv $(VENV); \
	fi
	. $(VENV)/bin/activate
endef

run: ensure_venv install
	$(PYTHON) main.py

install: ensure_venv requirements.txt
	. $(VENV)/bin/activate && \
	$(PIP) install --upgrade pip && \
	$(PIP) install -r requirements.txt

ensure_venv:
	$(ensure_venv)

lint: ensure_venv install
	$(PYTHON) -m pylint --disable=missing-module-docstring,broad-except,no-else-return,inconsistent-return-statements *.py
	$(PYTHON) -m flake8 *.py
	
check_format: ensure_venv install
	$(PYTHON) -m black --check --line-length 88  **/*.py

format: ensure_venv install
	$(PYTHON) -m black --line-length 88 **/*.py *.py

clean: ensure_venv install
	$(PYTHON) -m pyclean .
	rm -f logs/*

test: ensure_venv install
	@export TEST_MODE=$(TEST_MODE); \
	PYTHONPATH=.:$(PYTHONPATH) $(PYTHON) -m unittest discover -s tests -p 'test_*.py'

