validate-datasets:
	@echo "Validate that all datasets are correctly formatted"
	@echo "Note that this command assumed you have the 'dfm-data' folder and the github repo folder 'danish-foundation-models' during UCloud setup"
	python data-processing/scripts/dataset_validator.py --dataset_folder /work/dfm-data/pre-training --datasheets_folder /work/danish-foundation-models/docs/datasheets

data-processing-install:
	@echo "Installing package and required dependencies"
	pip install -e "data-processing/.[dev,test,docs]"

lint: 
	@echo "Linting code"
	ruff check src --fix
	black .

docs-serve:
	@echo "Serving documentation"
	@echo "Make sure you have installed docs:"
	@echo "pip install -r docs/requirements.txt"
	mkdocs serve