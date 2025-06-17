# -*- mode: Makefile -*-

.SUFFIXES:
MAKEFLAGS += --warn-undefined-variables
.SHELLFLAGS := -euc

# Show a nice table of Make targets.
# Generate it by grepping through the Makefile for targets with a ## after them,
# and treat everything following ## as the description.
.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: cleandata
cleandata: ## Remove all data files
	rm -rf data/

.PHONY: cleandist
cleandist: ## Remove all distribution files
	rm -rf dist/

data/named-characters.html: ## Retrieve the named-characters.html file from WHATWG
	mkdir -p data/
	curl -o data/named-characters.html https://html.spec.whatwg.org/multipage/named-characters.html

dist/_manifest.yml: _manifest.yml
	mkdir -p dist/
	cp _manifest.yml dist/_manifest.yml

dist/package.yml: data/named-characters.html parser.py
	mkdir -p dist/
	python3 parser.py data/named-characters.html --output dist/package.yml

dist/README.md: README.espansopackage.md
	mkdir -p dist/
	cp README.espansopackage.md dist/README.md

.PHONY: dist
dist: dist/_manifest.yml dist/package.yml dist/README.md ## Create the distribution directory for the package
