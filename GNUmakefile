# -*- mode: Makefile -*-

.SUFFIXES:
MAKEFLAGS += --warn-undefined-variables
.SHELLFLAGS := -euc

# Show a nice table of Make targets.
.PHONY: help
help: ## Show this help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: cleandata
cleandata: ## Remove all data files
	rm -rf data/

.PHONY: cleandist
cleandist: ## Remove all distribution files
	rm -rf dist/

data/named-characters.html:
	mkdir -p data/
	curl -o data/named-characters.html https://html.spec.whatwg.org/multipage/named-characters.html

.PHONY: data
data: data/named-characters.html ## Download the named characters HTML file from WHATWG

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
	@echo "Distribution files created in dist/"

.PHONY: install
install: dist ## Build the package and copy it to your Espanso config dir
	cp dist/package.yml "$$(espanso path config)"/match/named-html-entities.yml
	@echo "Package installed to Espanso config directory."
