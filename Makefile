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
	@echo TEST: input/blocks.wikidot
	./src/wikidot_to_html.py \
	< test/input/blocks.wikidot \
	> output/blocks.html
	diff test/expected.output/blocks.html output/blocks.html

.PHONY: test.block-quote
test.block-quote: | output
	@echo TEST: input/block-quote.wikidot
	./src/wikidot_to_html.py \
	< test/input/block-quote.wikidot \
	> output/block-quote.html
	diff test/expected.output/block-quote.html output/block-quote.html

.PHONY: test.comment
test.comment: | output
	@echo TEST: input/comment.wikidot
	./src/wikidot_to_html.py \
	< test/input/comment.wikidot \
	> output/comment.html
	diff test/expected.output/comment.html output/comment.html

.PHONY: test.div
test.div: | output
	@echo TEST: input/div.wikidot
	./src/wikidot_to_html.py \
	< test/input/div.wikidot \
	> output/div.html
	diff test/expected.output/div.html output/div.html

.PHONY: test.font
test.font: | output
	@echo TEST: input/font.wikidot
	./src/wikidot_to_html.py \
	< test/input/font.wikidot \
	> output/font.html
	diff test/expected.output/font.html output/font.html

.PHONY: test.headers
test.headers: | output
	@echo TEST: input/headers.wikidot
	./src/wikidot_to_html.py \
	< test/input/headers.wikidot \
	> output/headers.html
	diff test/expected.output/headers.html output/headers.html

.PHONY: test.html-entities
test.html-entities: | output
	@echo TEST: input/html-entities.wikidot
	./src/wikidot_to_html.py \
	< test/input/html-entities.wikidot \
	> output/html-entities.html
	diff test/expected.output/html-entities.html output/html-entities.html

.PHONY: test.image
test.image: | output
	@echo TEST: input/image.wikidot
	./src/wikidot_to_html.py \
	< test/input/image.wikidot \
	> output/image.html
	diff test/expected.output/image.html output/image.html

.PHONY: test.links
test.links: | output
	@echo TEST: input/links.wikidot
	./src/wikidot_to_html.py \
	< test/input/links.wikidot \
	> output/links.html
	diff test/expected.output/links.html output/links.html

.PHONY: test.lists
test.lists: | output
	@echo TEST: input/lists.wikidot
	./src/wikidot_to_html.py \
	< test/input/lists.wikidot \
	> output/lists.html
	diff test/expected.output/lists.html output/lists.html

.PHONY: test.literal
test.literal: | output
	@echo TEST: input/literal.wikidot
	./src/wikidot_to_html.py \
	< test/input/literal.wikidot \
	> output/literal.html
	diff test/expected.output/literal.html output/literal.html

.PHONY: test.math
test.math: | output
	@echo TEST: input/math.wikidot
	./src/wikidot_to_html.py \
	< test/input/math.wikidot \
	> output/math.html
	diff test/expected.output/math.html output/math.html

.PHONY: test.phrase
test.phrase: | output
	@echo TEST: input/phrase.wikidot
	./src/wikidot_to_html.py \
	< test/input/phrase.wikidot \
	> output/phrase.html
	diff test/expected.output/phrase.html output/phrase.html

.PHONY: test.table
test.table: | output
	@echo TEST: input/table.wikidot
	./src/wikidot_to_html.py \
	< test/input/table.wikidot \
	> output/table.html
	diff test/expected.output/table.html output/table.html

.PHONY: test.whitespace
test.whitespace: | output
	@echo TEST: input/whitespace.wikidot
	./src/wikidot_to_html.py \
	< test/input/whitespace.wikidot \
	> output/whitespace.html
	diff test/expected.output/whitespace.html output/whitespace.html


# no test.div
.PHONY: test
test: test.blocks test.block-quote test.comment test.font test.headers test.html-entities test.image test.links test.lists test.literal test.math test.math test.phrase test.table test.whitespace

.PHONY: all
all:
	echo 'Run tests with "make test"'

.PHONY: pep8
pep8:
	find . -name '*.py' | xargs pep8

.PHONY: pylint
pylint:
	find . -name '*.py' | xargs pylint -d missing-docstring
