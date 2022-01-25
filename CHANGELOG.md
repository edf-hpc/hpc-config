# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [3.1.0] - 2022-01-25

### Added
- h-c-push: factorize openssl cmd generation
- h-c-push: use password derivation when available

### Fixed
- h-c-push: handle failed openssl command
- h-c-push: remove double logging handler
- h-c-apply: remove duplicate PUPPET_*_PATH vars

### Removed
- h-c-push: remove useless comments

## [3.0.1]

### Fixed
- new node classifier as an explicit given role name
- backport features introduced in rhel8
- variabilized redhat versus debian puppet paths
- apply: Use puppet upstream packaging paths

## [2.0.6]

### Fixed
- h-c-apply: Support centos as well as redhat

## [2.0.5]

### Fixed
- h-c-apply: Fix connection error for scibian8

## [2.0.4]

### Fixed
- h-c-push: fix "Unknown digest" error in openssl call with -md option

## [2.0.3]

### Fixed
- Fix mismatching version and tag in 2.0.1 

## [2.0.2]

### Changed
- h-c-push: use digest type sha256 for openssl command instead of the default
  type, for encryption and decryption of files

## [2.0.1]

### Fixed
- h-c-push: use os.walk with fnmatch to find encrypted files

## [2.0.0]

### Changed
- h-c-{push,apply}: propagate cluster-node-classifier ENC script input file
  instead of external fact YAML file
- h-c-push: generate separate configuration environment for all areas, with
  on-the-fly/parallel re-encryptions.
- h-c-apply: download the configuration environment of a specific area

### Added
- Introduce new script cluster-node-classifier designed to be used as ENC
- h-c-apply: generate static external fact for private\_files\_dir
- h-c-push: add ability to list pushed environments

### Fixed
- h-c-apply: fix retry loop when fixed source port (<1024) is already used by
  another TCP connection.
- h-c-apply: add missing explanation in manpage for output and TTY (fix #3)

## [1.1.7] - 2018-07-20

### Changed
- h-c-apply: be verbose by default when stdout is TTY

## [1.1.6] - 2018-01-16

### Changed
- h-c-push: S3: Not removing remote files but update

## [1.1.5] - 2017-10-05

### Changed
- h-c-push Optimize paramiko and set remote file modes
- h-c-push Optimize S3 push

## [1.1.4] - 2017-08-17

### Changed
- h-c-apply: More verbose end status output
- h-c-apply: Read parameters from kernel command line

### Fixed
- h-c-apply: Fix profile option parsing

## [1.1.3] - 2017-08-08

### Changed
- h-c-apply: Ensure directory exists before applying perms

## [1.1.2] - 2017-08-08

### Changed
- h-c-apply Set perms on /etc/puppet/{secure,environment}
- manpage: Update hpc-config-apply with sftp
- scripts: h-c-apply: remove env by default after run, --keep option

### Fixed
- h-c-apply Pep8 fixes

## [1.1.1] - 2017-07-21

### Added
- h-c-apply: Add a --profile option
- init: Add an init script for EL6
- rpm: Add spec file for hpc-config-apply

### Changed
- h-c-apply Use en_US.UTF-8 locale on RH
- h-c-push Optimize sftp push by not repeating checks

## [1.0.1] - 2017-04-18

### Fixed
- h-c-push Hide python warnings for deprecation and future

## [1.0.0] - 2017-04-06

### Added
- h-c-push Add support for SFTP servers
- conf push.conf: add sftp and posix sections

### Changed
- h-c-push: Explicitely set perms (posix)

### Fixed
- fix locate interpolation in hash keys

## [0.11] - 2017-02-20

### Changed
- explain why conf_copy in comment
- follow symlinks for h-c-push in s3

### Fixed
- handle symlinks on dir in h-c-push
- fix licensing headers

## [0.10] - 2016-12-09

### Added
- add pre-built manpages

## [0.9] - 2016-11-24

### Added
- h-c-apply Add --tags and --dry-run parameters

### Changed
- h-c-apply forward puppet exit code

## [0.8] - 2016-10-18

### Added
- h-c-apply permit to set TMPDIR for puppet run

### Changed
- h-c-push Add warnings when dirs are missing
- h-c-apply Fail on HTTP status >= 400

### Fixed
- h-c-push Fix indent width

## [0.7] - 2016-10-03
  * scripts h-c-apply Create parent directory for fact file

## [0.6] - 2016-09-28
  * scripts h-c-apply Clean source and skip environment if null source
  * scripts h-c-push On S3 make sure all directories are created

## [0.5] - 2016-09-28

### Added
- h-c-push Add S3 support

### Fixed
- h-c-a coding style
- h-c-a Set some headers and do a proper http request

## [0.4] - 2016-09-22

### Fixed
- h-c-a Don't stupidly loop on all ports

## [0.3] - 2016-09-20

### Changed
- h-c-a Use DEFAULT section values as... defaults
- h-c-a Skip retrievals if sources are undefined

### Removed
- Remove modules_3rdparty from push conf

### Fixed
- scripts h-c-a Fix infinite loop if connection to http fails

## [0.2] - 2016-09-15

### Added
- Initial release
