# hpc-config

## Overview

hpc-config is a suite of utilities to ease deployment of
[Puppet-HPC](https://github.com/edf-hpc/puppet-hpc) configuration management
stack.

## License

hpc-config is distributed under the GNU General Public License version 3.0 or
later (GPLv3+).

## Release

Steps to produce release `$VERSION` (ex: `2.1.3`):

Update `CHANGELOG.md` to move entries under the `[Unrelease]` into a new
release section. Then run:

```
git add CHANGELOG.md
git commit -m "Release $VERSION"
git tag -a v$VERSION -m "Release $VERSION"
```

Then, merge the `master` branch into the `rpm` branch. Update the `Version` and
`%changelog` of `hpc-config.spec` and run:

```
git add hpc-config.spec
git commit -m "RPM release $VERSION-1"
```

Finally push all the branches and tags.

To generate a tarball, run:

```
git archive --format=tar.gz --prefix=hpc-config-$VERSION/ \
    v$VERSION > ../hpc-config-$VERSION.tar.gz
```
