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
	./src/wikidot_to_html.py \
	< test/input/blocks.hpwiki \
	> output/blocks.html
	diff test/expected.output/blocks.html output/blocks.html

.PHONY: test.blocks
test.block-quote: | output
	@echo TEST: input/block-quote.hpwiki
	./src/wikidot_to_html.py \
	< test/input/block-quote.hpwiki \
	> output/block-quote.html
	diff test/expected.output/block-quote.html output/block-quote.html

.PHONY: test.comment
test.comment: | output
	@echo TEST: input/comment.hpwiki
	./src/wikidot_to_html.py \
	< test/input/comment.hpwiki \
	> output/comment.html
	diff test/expected.output/comment.html output/comment.html

.PHONY: test.blocks
test.div: | output
	@echo TEST: input/div.hpwiki
	./src/wikidot_to_html.py \
	< test/input/div.hpwiki \
	> output/div.html
	diff test/expected.output/div.html output/div.html

.PHONY: test.font
test.font: | output
	@echo TEST: input/font.hpwiki
	./src/wikidot_to_html.py \
	< test/input/font.hpwiki \
	> output/font.html
	diff test/expected.output/font.html output/font.html

.PHONY: test.headers
test.headers: | output
	@echo TEST: input/headers.hpwiki
	./src/wikidot_to_html.py \
	< test/input/headers.hpwiki \
	> output/headers.html
	diff test/expected.output/headers.html output/headers.html

.PHONY: test.html-entities
test.html-entities: | output
	@echo TEST: input/html-entities.hpwiki
	./src/wikidot_to_html.py \
	< test/input/html-entities.hpwiki \
	> output/html-entities.html
	diff test/expected.output/html-entities.html output/html-entities.html

.PHONY: test.image
test.image: | output
	@echo TEST: input/image.hpwiki
	./src/wikidot_to_html.py \
	< test/input/image.hpwiki \
	> output/image.html
	diff test/expected.output/image.html output/image.html

.PHONY: test.links
test.links: | output
	@echo TEST: input/links.hpwiki
	./src/wikidot_to_html.py \
	< test/input/links.hpwiki \
	> output/links.html
	diff test/expected.output/links.html output/links.html

.PHONY: test.lists
test.lists: | output
	@echo TEST: input/lists.hpwiki
	./src/wikidot_to_html.py \
	< test/input/lists.hpwiki \
	> output/lists.html
	diff test/expected.output/lists.html output/lists.html

.PHONY: test.literal
test.literal: | output
	@echo TEST: input/literal.hpwiki
	./src/wikidot_to_html.py \
	< test/input/literal.hpwiki \
	> output/literal.html
	diff test/expected.output/literal.html output/literal.html

.PHONY: test.math
test.math: | output
	@echo TEST: input/math.hpwiki
	./src/wikidot_to_html.py \
	< test/input/math.hpwiki \
	> output/math.html
	diff test/expected.output/math.html output/math.html

.PHONY: test.table
test.table: | output
	@echo TEST: input/table.hpwiki
	./src/wikidot_to_html.py \
	< test/input/table.hpwiki \
	> output/table.html
	diff test/expected.output/table.html output/table.html

# no test.div
.PHONY: test
test: test.blocks test.block-quote test.comment test.font test.headers test.html-entities test.image test.links test.lists test.literal test.math test.math test.table

.PHONY: all
all:
	echo 'Run tests with "make test"'

.PHONY: pep8
pep8:
	find . -name '*.py' | xargs pep8

.PHONY: pylint
pylint:
	find . -name '*.py' | xargs pylint -d missing-docstring
