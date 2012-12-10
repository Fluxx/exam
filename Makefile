VERSION = $(shell python setup.py --version)

test:
	python setup.py nosetests

release:
	git tag $(VERSION)
	git push origin $(VERSION)
	python setup.py sdist upload

watch:
	bundle exec guard

.PHONY: test release watch
