build-docs:
	@echo "--- 📚 Building docs ---"
	@echo "Builds the docs and puts them in the 'site' folder"
	@echo "You might need to also update the table with the desc. stats you can do this by running 'make update-table-in-docs'"
	uv run mkdocs build

view-docs:
	@echo "--- 👀 Viewing docs ---"
	uv run mkdocs serve
	