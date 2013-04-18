# Makefile

SHELL := /bin/bash

.PHONY: all build run test

# main

all: build

build: bootstrap.py \
	bin/buildout \
	bin/localbitcoins

run:
	bin/main

test:
	bin/test

clean:
	rm -rf bin lib bootstrap.py localbitcoins.egg-info

# helpers

bootstrap.py:
	wget http://downloads.buildout.org/1/bootstrap.py

bin/buildout:
	mkdir -p lib/buildout
	mkdir -p lib/buildout/downloads
	python bootstrap.py

bin/localbitcoins:
	bin/buildout -N
	touch $@
