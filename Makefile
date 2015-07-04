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
test: test.blocks test.code test.code2 test.code3 test.div test.div2 test.font
test: test.headers test.html-entities test.image test.links
test: test.lists test.lists1 test.lists2 test.lists4
test: test.literal test.phrase test.table test.whitespace

.PHONY: tests.failing
tests.failing: test.block-quote
tests.failing: test.span
tests.failing: test.math
tests.failing: test.table2

.PHONY: tests.optional
tests.optional: test.non-ascii
tests.optional: test.comment
tests.optional: test.list3
tests.optional: test.smart-quotes test.smart-quotes2

.PHONY: all
all:
	echo 'Run tests with "make test"'

.PHONY: pep8
pep8:
	find . -name '*.py' | xargs pep8

.PHONY: pylint
pylint:
	find . -name '*.py' | xargs pylint -d missing-docstring
