test: ## Run tests
	pytest src

lint: ## Format code
	pre-commit run --all-files

type-check: ## Type-check code
	pyright src

pr: ## Run relevant tests before PR
	make lint
	make type-check
	make test
	gh pr create -w