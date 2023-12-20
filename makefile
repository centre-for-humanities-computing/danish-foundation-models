install:
	@echo "Installing package and required dependencies"
	pip install -e .[dev,test,docs]

test:
	@echo "Running tests"
	pytest src

lint: 
	@echo "Linting code"
	ruff check src --fix
	black .

type-check:
	@echo "Type-checking code-base"
	pyright src

validate:
	@echo "Running all checks"
	make lint
	make type-check
	make test

pr: 
	@echo "Running relevant checks before PR"
	make validate
	gh pr create -w

docs-serve:
	@echo "Serving documentation"
	@echo "Make sure you have installed docs:"
	@echo "pip install -e .[docs]"
	mkdocs serve