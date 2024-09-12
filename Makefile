virenv:
	@echo "START: creating conda venv"
	conda env create -f environment.yml
	@echo "FINISH: creating conda venv"

.PHONY: install
install:
	python -m pip install --upgrade pip && \
	pip install --upgrade pip setuptools wheel && \
	python -m pip install -e . && \
	pre-commit install

	@echo "Package installed successfully"
	@echo "------------------------------"
	@echo "Adding BayesianOptimization as a submodule"
	git submodule add https://github.com/bayesian-optimization/BayesianOptimization.git _deps/bayesian-optimization
	cd _deps/bayesian-optimization && git checkout dc4e8ef21835d694c2debc82c6d509cfa419d0f6

	pip install -e _deps/bayesian-optimization
	@echo "submodule added successfully"

test:
	python -m unittest discover tests
