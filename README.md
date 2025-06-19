# espanso-named-html-entity

This repo builds the Named HTML Entity package for Espanso.

Running `make` by itself prints help:

```console
> make
cleandata            Remove all data files
cleandist            Remove all distribution files
data                 Download the named characters HTML file from WHATWG
dist                 Create the distribution directory for the package
help                 Show this help
install              Build the package and copy it to your Espanso config dir
```

See [./README.espansopackage.md](./README.espansopackage.md) for the user-facing package README.

## Data

The [named-characters.html](./data/named-characters.html) file is pulled down from WHATWG and then committed to the repo; to refresh it, run:

```sh
make cleandata data/named-characters.html
```

## Testing

To try this out in espanso without installing the package from the hub:

```sh
make install
```

## Submitting a new version to the Espanso Hub

* If you want to pull a new copy of the named entities data, run `make cleandata` first
* Determine the version and write to `_manifest.yml`
* Build with `make build`
* Copy all of `dist/` to a checkout of the [hub](https://github.com/espanso/hub), under
  `packages/named-html-entities/VERSION` (must match version in `_manifest.yml`)
* Make a PR to the upstream [hub](https://github.com/espanso/hub) repo
