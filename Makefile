#!/usr/bin/make
#
all: run

BUILDOUT_FILES = bin/buildout buildout.cfg buildout.d/*.cfg

.PHONY: bootstrap buildout run test cleanall

buildout: bootstrap
	bin/buildout -t 5

bootstrap:
	virtualenv -p python2 .
	./bin/pip install -r requirements.txt

run: buildout
	bin/instance fg

test:
	rm -fr htmlcov
	bin/test

cleanall:
	rm -fr bin include lib local share htmlcov develop-eggs downloads eggs parts .installed.cfg .mr.developper.cfg .git/hooks/pre-commit
