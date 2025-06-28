.PHONY: build
build:
	python3 -m build

.PHONY: publish
publish:
	python3 -m twine upload --repository testpypi dist/* --verbose

.PHONY: clean
clean:
	rm -rf dist src/*.egg-info

.PHONY: build-publish
build-publish: 
	clean build publish

.PHONY: spin-env
spin-env:
	python3 -m venv .env
	.env/bin/pip install --upgrade pip
	source ./.env/bin/activate