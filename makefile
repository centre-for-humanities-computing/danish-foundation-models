install:
	pip install -e .[dev,test,docs]

test: ## Run tests
	pytest src

lint: ## Format code
	ruff check src --fix
	black .

type-check: ## Type-check code
	pyright src

validate: ## Run all checks
	make lint
	make type-check
	make test

pr: ## Run relevant tests before PR
	make validate
	gh pr create -w

docs-serve:  ## build and serve documentation
	# make sure you have installed docs:
	# pip install -e .[docs]
	mkdocs serve