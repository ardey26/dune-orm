.PHONY: build
build:
	python3 -m build

.PHONY: publish
publish:
	python3 -m twine upload --repository testpypi dist/* --verbose