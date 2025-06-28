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