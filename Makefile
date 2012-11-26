VERSION = $(shell python -c 'import exam; print exam.__version__')

test:
	python setup.py nosetests

release:
	git tag $(VERSION)
	git push origin $(VERSION)
	python setup.py sdist upload

.PHONY: test release