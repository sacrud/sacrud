all: test

test: 
	. ../../env/bin/activate; python setup.py test

coverage:
	. ../../env/bin/activate; nosetests --cover-package=sacrud --cover-erase --with-coverage

run:
	. ../../env/bin/activate; pserve development.ini
     
shell:
	. ../../env/bin/activate; pshell development.ini

	
