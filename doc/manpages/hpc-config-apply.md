% hpc-config-apply (1)

# NAME

hpc-config-apply - download and apply a puppet-hpc configuration

# SYNOPSIS

       hpc-config-apply [-h] [--dry-run] [--keep] [--no-kernel-args]
                        [--profile] [--config [CONFIG_FILE]]
                        [--source [SOURCE]] [--environment [ENVIRONMENT]]
                        [--tmpdir [TMPDIR]]
                        [--deploy-step [{production,usbdisk}]]
                        [--keys-source [KEYS_SOURCE]] [--tags [TAGS]]
                        [--verbose]

# DESCRIPTION

hpc-config-apply downloads a Puppet configuration and all the related
files via HTTP and applies this configuration on a cluster node.

# OPTIONS

    -h, --help            show this help message and exit
    --dry-run             Don't actually perform configuration (still downloads
                          env).
    --keep, -K            Keep local data at the end of the run.
    --no-kernel-args, -N  Disable parsing of kernel cmdline arguments.
    --profile             Profile the puppet run.
    --config [CONFIG_FILE], -c [CONFIG_FILE]
                          Configuration file
    --source [SOURCE], -s [SOURCE]
                          Configuration source URL
    --environment [ENVIRONMENT], -e [ENVIRONMENT]
                          Environment name
    --tmpdir [TMPDIR], -t [TMPDIR]
                          Change TMPDIR env for puppet run.
    --deploy-step [{production,usbdisk}], -d [{production,usbdisk}]
                          Deploy step
    --keys-source [KEYS_SOURCE], -k [KEYS_SOURCE]
                          Secret keys source
    --tags [TAGS]         Puppet tags (comma separated list)
    --verbose, -v         More output, can be specified multiple times.


# PARAMETERS

`hpc-config-apply` has six configuration sources considered in this
order:
 * Command line arguments
 * Kernel command line
 * Configuration file environment section
 * Configuration file DEFAULT section
 * Environment file (for `tmpdir`)
 * Application default

The kernel command line parameters can be specified with the syntax:
`hpc_conf.environment=test`. Boolean can be specified without the '`=`'
character to mean True or more directly `hpc_conf.keep=True`. Kernel command
line is read from the file `/proc/cmdline`. It can be used to load an alternate
environment on a diskless node.

If kernel command line parameters should be ignored for a particular run, the
command line option `--no-kernel-args` can be used.

The supported parameters and there defaults are:
 * dry_run (boolean): False
 * keep (boolean): False
 * no_kernel_args (boolean): False
 * profile (boolean): False
 * config (string): `'/etc/hpc-config.conf'`
 * source (string): None
 * environment (string): `'production'`
 * tmpdir (string): TMPDIR environment variable
 * deploy_step (string): `'production'`
 * keys_source (string): None
 * tags (string): None
 * verbosity (int): 0

# CONFIGURATION FILE

The default configuration file is installed at `/etc/hpc-config.conf` and it
is a simple text file using the [INI file format](http://en.wikipedia.org/wiki/INI_file).
This file has a basic structure composed of sections, properties, and values.
The lines starting with a semi-colon are commentaries and they're ignored.
Each section describes an environment, the '[DEFAULT]' section is used when no
environment is specified via the '-e' option.
In each section, each option of the command line can be defined (except
config file).
Here is an example of a typical file with only a '[DEFAULT]' section:

    [DEFAULT]
    environment=production
    source=http://masternode/hpc-config
    keys_source=http://masternode/secret

# DATA PROTECTION

The Puppet environment data is removed after the run by default. The `--keep`
option can be used to preserve those data on the node after the run.

The permissions of directories containing sensitive data (keys and Puppet
environment are modified to make them only readable by root.

# EXAMPLES

To simply apply the default puppet environment:

    hpc-config-apply

To apply the 'test' environment in verbose mode:

    hpc-config-apply -v -e test

# SEE ALSO

hpc-config-push(1)
