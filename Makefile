VERSION = $(shell python -c 'import exam; print exam.__version__')

test:
	python setup.py nosetests

release:
	git tag $(VERSION)
	git push origin $(VERSION)
	python setup.py sdist upload

watch:
	bundle exec guard

.PHONY: test release watch