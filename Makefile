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
test: test.blockquote test.blockquote2 test.blockquote3 test.blockquote4
test: test.blocks test.code test.code2 test.code3 test.code4
test: test.comment test.div test.div2 test.font
test: test.headers test.html-entities test.image test.links test.links2
test: test.lists test.lists1 test.lists2 test.lists4
test: test.literal test.math test.math2 test.math4
test: test.p test.phrase test.span
test: test.table test.table3 test.table4 test.table5 test.table6 test.whitespace

.PHONY: tests.failing
tests.failing: test.table2 test.table7

.PHONY: tests.optional
tests.failing: test.math3
tests.optional: test.non-ascii
tests.optional: test.comment2
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
