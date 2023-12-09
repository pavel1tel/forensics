lint:
	ruff check --fix app \
	&& black app \
	&& mypy app

clean:
	rm -rf tmp
	rm -rf temp

build:
	pyinstaller --name image_scan --onefile --add-data "model/model_c1.pth:model" app/cli/main.py
