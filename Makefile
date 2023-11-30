virenv:
	conda env create -f environment.yaml

.PHONY: install
install:
	python -m pip install --upgrade pip && \
	pip install --upgrade pip setuptools wheel && \
	python -m pip install -e . && \
	pre-commit install
	@echo "Package installed successfully"

test:
	python -m unittest discover tests
