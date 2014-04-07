all: test

test:
	python runtest.py

run:
	pserve development.ini

shell:
	pshell development.ini
