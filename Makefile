.PHONY: all clean lint type test test-cov

CMD:=poetry run
PYMODULE:=backup

all: type format lint

fix: format lint-fix

lint: 
	$(CMD) ruff check $(PYMODULE)

lint-fix: 
	$(CMD) ruff check --fix $(PYMODULE)

format:
	$(CMD) ruff format $(PYMODULE)

format-check:
	$(CMD) ruff format --check $(PYMODULE)

type: 
	$(CMD) mypy $(PYMODULE)

clean:
	git clean -Xdf # Delete all files in .gitignore