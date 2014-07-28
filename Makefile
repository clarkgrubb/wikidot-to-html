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
	@echo TEST: input/blocks.hpwiki
	./src/hyperpolywiki_to_html.py \
	< test/input/blocks.hpwiki \
	> output/blocks.html
	diff test/expected.output/blocks.html output/blocks.html

.PHONY: test.blocks
test.block-quote: | output
	@echo TEST: input/block-quote.hpwiki
	./src/hyperpolywiki_to_html.py \
	< test/input/block-quote.hpwiki \
	> output/block-quote.html
	diff test/expected.output/block-quote.html output/block-quote.html


.PHONY: test.headers
test.headers: | output
	@echo TEST: input/headers.hpwiki
	./src/hyperpolywiki_to_html.py \
	< test/input/headers.hpwiki \
	> output/headers.html
	diff test/expected.output/headers.html output/headers.html

.PHONY: test.table
test.table: | output
	@echo TEST: input/table.hpwiki
	./src/hyperpolywiki_to_html.py \
	< test/input/table.hpwiki \
	> output/table.html
	diff test/expected.output/table.html output/table.html

.PHONY: test.links
test.links: | output
	@echo TEST: input/links.hpwiki
	./src/hyperpolywiki_to_html.py \
	< test/input/links.hpwiki \
	> output/links.html
	diff test/expected.output/links.html output/links.html

.PHONY: test.literal
test.literal: | output
	@echo TEST: input/literal.hpwiki
	./src/hyperpolywiki_to_html.py \
	< test/input/literal.hpwiki \
	> output/literal.html
	diff test/expected.output/literal.html output/literal.html

.PHONY: test.math
test.math: | output
	@echo TEST: input/math.hpwiki
	./src/hyperpolywiki_to_html.py \
	< test/input/math.hpwiki \
	> output/math.html
	diff test/expected.output/math.html output/math.html

.PHONY: test.font
test.font: | output
	@echo TEST: input/font.hpwiki
	./src/hyperpolywiki_to_html.py \
	< test/input/font.hpwiki \
	> output/font.html
	diff test/expected.output/font.html output/font.html

.PHONY: test.comment
test.comment: | output
	@echo TEST: input/comment.hpwiki
	./src/hyperpolywiki_to_html.py \
	< test/input/comment.hpwiki \
	> output/comment.html
	diff test/expected.output/comment.html output/comment.html

.PHONY: test.image
test.image: | output
	@echo TEST: input/image.hpwiki
	./src/hyperpolywiki_to_html.py \
	< test/input/image.hpwiki \
	> output/image.html
	diff test/expected.output/image.html output/image.html

.PHONY: test.math
test.math: | output
	@echo TEST: input/math.hpwiki
	./src/hyperpolywiki_to_html.py \
	< test/input/math.hpwiki \
	> output/math.html
	diff test/expected.output/math.html output/math.html

.PHONY: test
test: test.blocks test.block-quote test.headers test.table test.links test.literal test.math test.font test.comment test.image test.math

.PHONY: all
all:
	echo 'Run tests with "make test"'

.PHONY: pep8
pep8:
	find . -name '*.py' | xargs pep8

.PHONY: pylint
pylint:
	find . -name '*.py' | xargs pylint -d missing-docstring
