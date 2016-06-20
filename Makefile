lint:
	pep8 --ignore=E303,E251,E201,E202 ./fake --max-line-length=140
	find ./fake -name '*.py' | xargs pyflakes

install:
	python setup.py install
