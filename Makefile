lint:
	ruff check --fix app \
	&& black app \
	&& mypy app
