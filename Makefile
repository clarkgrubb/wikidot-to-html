MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:

output:
	mkdir -p $@

test.%: | output
	@echo TEST: input/$*.wikidot
	./src/wikidot_to_html.py \
	< test/input/$*.wikidot \
	> output/$*.html
	diff test/expected.output/$*.html output/$*.html

.PHONY: test
test: test.blocks test.code2 test.div test.font test.headers
test: test.html-entities test.image test.links
test: test.lists test.lists1 test.lists2 test.lists4
test: test.literal
test: test.phrase test.table test.whitespace

.PHONY: tests.failing
tests.failing: test.block-quote test.code
tests.failing: test.comment
tests.failing: test.list3
tests.failing: test.math test.non-ascii
tests.failing: test.smart-quotes test.smart-quotes2
tests.failing: test.span
tests.failing: test.table2

.PHONY: all
all:
	echo 'Run tests with "make test"'

.PHONY: pep8
pep8:
	find . -name '*.py' | xargs pep8

.PHONY: pylint
pylint:
	find . -name '*.py' | xargs pylint -d missing-docstring
