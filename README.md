# espanso-named-html-entity

This repo builds the Named HTML Entity package for Espanso.

The makefile prints help:

```sh
make
```

## Building

To build:

```sh
make dist
```

The resulting `dist/` directory should be copied into a fork of the [hub](https://github.com/espanso/hub) repository, and a pull request opened to update the hub.

The [named-characters.html](./data/named-characters.html) file is pulled down from WHATWG; to refresh it, run:

```sh
make cleandata data/named-characters.html
```

## Testing

To try this out in espanso without installing the package from the hub:

```sh
make dist
cp dist/package.yml $(espanso path config)/match/named-html-elements.yml
```
