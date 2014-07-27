MAKEFLAGS += --warn-undefined-variables
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:

output:
	mkdir -p $@

.PHONY: test.blocks
test.blocks: | output
	./src/hyperwiki_to_html.py \
	< test/input/blocks.hyperwiki \
	> output/blocks.html
	diff test/expected.output/blocks.html output/blocks.html

.PHONY: test
test: test.blocks

.PHONY: all
all:
	echo 'Run tests with "make test"'

.PHONY: pep8
pep8:
	find . -name '*.py' | xargs pep8

.PHONY: pylint
pylint:
	find . -name '*.py' | xargs pylint -d missing-docstring
