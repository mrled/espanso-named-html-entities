# espanso-named-html-entity

This repo builds the Named HTML Entity package for Espanso.

To build:

```sh
make dist
```

The resulting `dist/` directory should be copied into a fork of the [hub](https://github.com/espanso/hub) repository, and a pull request opened to update the hub.

The [named-characters.html](./data/named-characters.html) file is pulled down from WHATWG; to refresh it, run `make cleandata data/named-characters.html`.

Run `make` on its own for help from the makefile.
