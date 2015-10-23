all: test

test:
	python setup.py test

coverage: test
	coverage html

clean:
	find . -name '*.pyc' -delete
	rm -rf build *.egg* dist __pycache__ .cache
