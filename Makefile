MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := all
.DELETE_ON_ERROR:
.SUFFIXES:

max_line_length = 150

ve:
	virtualenv --python=python3 ve
	. ve/bin/activate && pip install -r requirements.txt

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
test-failing: test.literal6
test-failing: test.table2 test.table7

.PHONY: test-optional
# nested comment:
test-optional: test.comment2
# [[ul]] style lists:
test-optional: test.lists3
# inline math: [[$ \infty $]]
test-optional: test.math3
# ndash, mdash, ellipsis, guillemet, goosefeet
test-optional: test.non-ascii
test-optional: test.smart-quotes test.smart-quotes2

.PHONY: all
all:
	echo 'Run tests with "make test"'

.PHONY: pycodestyle
pycodestyle: ve
	. ve/bin/activate && find src -name '*.py' | xargs pycodestyle --max-line-length=$(max_line_length)

.PHONY: pylint
pylint: ve
	. ve/bin/activate && find src -name '*.py' | xargs pylint -d missing-docstring
