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
test: test-passing

.PHONY: test-passing
test-passing: test.blockquote test.blockquote2 test.blockquote3 test.blockquote4
test-passing: test.blocks
test-passing: test.code test.code2 test.code3 test.code4 test.code5
test.passing: test.comment
test.passing: test.div test.div2
test-passing: test.font test.font2
test-passing: test.headers
test-passing: test.html-entities
test-passing: test.image
test-passing: test.links test.links2
test-passing: test.lists test.lists1 test.lists2 test.lists4
test-passing: test.literal test.literal2 test.literal3 test.literal4 test.literal5
test-passing: test.math test.math2 test.math4
test-passing: test.p
test-passing: test.phrase
test-passing: test.span
test-passing: test.table test.table3 test.table4 test.table5 test.table6 test.table8 test.table9
test-passing: test.whitespace

.PHONY: test-failing
test-failing: test.comment2
test-failing: test.lists3
test-failing: test.literal6
test-failing: test.math3
test-failing: test.non-ascii
test-failing: test.smart-quotes test.smart-quotes2
test-failing: test.table2 test.table7

.PHONY: all
all:
	echo 'Run tests with "make test"'

.PHONY: pep8
pep8:
	find . -name '*.py' | xargs pep8

.PHONY: pylint
pylint:
	find . -name '*.py' | xargs pylint -d missing-docstring
