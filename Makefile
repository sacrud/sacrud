all: test

test:
	python setup.py test

coverage: test
	coverage html

clean:
	find . -name '*.pyc' -delete
