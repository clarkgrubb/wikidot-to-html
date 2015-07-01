MAKEFLAGS += --warn-undefined-variables
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
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

.PHONY: test.code
test.code: | output
	@echo TEST: input/code.wikidot
	./src/wikidot_to_html.py \
	< test/input/code.wikidot \
	> output/code.html
	diff test/expected.output/code.html output/code.html

.PHONY: test.collapsible-block
test.collapsible-block: | output
	@echo TEST: input/collapsible-block.wikidot
	./src/wikidot_to_html.py \
	< test/input/collapsible-block.wikidot \
	> output/collapsible-block.html
	diff test/expected.output/collapsible-block.html output/collapsible-block.html

.PHONY: test.comment
test.comment: | output
	@echo TEST: input/comment.wikidot
	./src/wikidot_to_html.py \
	< test/input/comment.wikidot \
	> output/comment.html
	diff test/expected.output/comment.html output/comment.html

.PHONY: test.definition-lists
test.definition-lists: | output
	@echo TEST: input/definition-lists.wikidot
	./src/wikidot_to_html.py \
	< test/input/definition-lists.wikidot \
	> output/definition-lists.html
	diff test/expected.output/definition-lists.html output/definition-lists.html

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

.PHONY: test.lists1
test.lists1: | output
	@echo TEST: input/lists1.wikidot
	./src/wikidot_to_html.py \
	< test/input/lists1.wikidot \
	> output/lists1.html
	diff test/expected.output/lists1.html output/lists1.html

.PHONY: test.lists2
test.lists2: | output
	@echo TEST: input/lists2.wikidot
	./src/wikidot_to_html.py \
	< test/input/lists2.wikidot \
	> output/lists2.html
	diff test/expected.output/lists2.html output/lists2.html

.PHONY: test.lists3
test.lists3: | output
	@echo TEST: input/lists3.wikidot
	./src/wikidot_to_html.py \
	< test/input/lists3.wikidot \
	> output/lists3.html
	diff test/expected.output/lists3.html output/lists3.html

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

.PHONY: test.non-ascii
test.non-ascii: | output
	@echo TEST: input/non-ascii.wikidot
	./src/wikidot_to_html.py \
	< test/input/non-ascii.wikidot \
	> output/non-ascii.html
	diff test/expected.output/non-ascii.html output/non-ascii.html

.PHONY: test.phrase
test.phrase: | output
	@echo TEST: input/phrase.wikidot
	./src/wikidot_to_html.py \
	< test/input/phrase.wikidot \
	> output/phrase.html
	diff test/expected.output/phrase.html output/phrase.html

.PHONY: test.smart-quotes
test.smart-quotes: | output
	@echo TEST: input/smart-quotes.wikidot
	./src/wikidot_to_html.py \
	< test/input/smart-quotes.wikidot \
	> output/smart-quotes.html
	diff test/expected.output/smart-quotes.html output/smart-quotes.html

.PHONY: test.smart-quotes2
test.smart-quotes2: | output
	@echo TEST: input/smart-quotes2.wikidot
	./src/wikidot_to_html.py \
	< test/input/smart-quotes2.wikidot \
	> output/smart-quotes2.html
	diff test/expected.output/smart-quotes2.html output/smart-quotes2.html

.PHONY: test.span
test.span: | output
	@echo TEST: input/span.wikidot
	./src/wikidot_to_html.py \
	< test/input/span.wikidot \
	> output/span.html
	diff test/expected.output/span.html output/span.html

.PHONY: test.table
test.table: | output
	@echo TEST: input/table.wikidot
	./src/wikidot_to_html.py \
	< test/input/table.wikidot \
	> output/table.html
	diff test/expected.output/table.html output/table.html

.PHONY: test.table2
test.table2: | output
	@echo TEST: input/table2.wikidot
	./src/wikidot_to_html.py \
	< test/input/table2.wikidot \
	> output/table2.html
	diff test/expected.output/table2.html output/table2.html

.PHONY: test.whitespace
test.whitespace: | output
	@echo TEST: input/whitespace.wikidot
	./src/wikidot_to_html.py \
	< test/input/whitespace.wikidot \
	> output/whitespace.html
	diff test/expected.output/whitespace.html output/whitespace.html

# no test.div
.PHONY: test
test: test.blocks test.block-quote test.comment test.font test.headers
test: test.html-entities test.image test.links test.lists test.literal
test: test.math test.phrase test.table test.whitespace

.PHONY: test.passing
test.passing: test.blocks test.font test.headers
test.passing: test.html-entities test.image test.links test.literal
test.passing: test.lists test.lists1 test.lists2 test.phrase test.table
test.passing: test.whitespace

.PHONY: test.failing
test.failing: test.block-quote test.code test.collapsible-block
test.failing: test.comment test.definition-lists test.div
test.failing: test.list3
test.failing: test.math test.non-ascii
test.failing: test.smart-quotes test.smart-quotes2
test.failing: test.span
test.failing: test.table2

.PHONY: all
all:
	echo 'Run tests with "make test"'

.PHONY: pep8
pep8:
	find . -name '*.py' | xargs pep8

.PHONY: pylint
pylint:
	find . -name '*.py' | xargs pylint -d missing-docstring
