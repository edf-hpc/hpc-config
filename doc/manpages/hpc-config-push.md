% hpc-config-push (1)

# NAME

hpc-config-push - push puppet-hpc configuration into central storage

# SYNOPSIS

    hpc-config-push [-h] [-d] [-c [CONF]] [-e [ENVIRONMENT]] [-V [VERSION]]
                    [--full-tmp-cleanup]

# DESCRIPTION

hpc-config-push makes available all the Puppet configuration into
a shared central storage to be used by hpc-config-apply on cluster nodes.
The pushed data includes the public puppet-hpc configuration, the
private data and files and packaged Puppet modules.

# OPTIONS

    -h, --help            show this help message and exit
    -d, --debug           Enable debug mode
    -c [CONF], --conf [CONF]
                          Path to the configuration file
    -e [ENVIRONMENT], --environment [ENVIRONMENT]
                          Name of the pushed environment
    -V [VERSION], --version [VERSION]
                          Version of the pushed config
    --full-tmp-cleanup    Full tmp dir cleanup.
    --enable-python-warnings
                          Enable some python warnings (deprecation and
                          future warnings are hidden by default)

# DIRECTORY LAYOUT

The source directories to be pushed can be placed anywhere in the
development machine as long as they are all at the same directory. The layout
of this directory should be like in the example below:

    some_directory/
    ├── private-data/
    │   ├── files/
    │   │   └── $CLUSTER/
    │   │       ├── cluster/
    │   │       └── $AREA/
    │   └── hieradata/
    │       ├── *.yaml
    │       └── $CLUSTER/
    │           ├── *.yaml
    │           ├── roles/
    │           │   └── *.yaml
    │           └── areas/
    │               └── $AREA.yaml
    └── puppet-hpc/

Where:

  - *$CLUSTER* is a cluster name,
  - *$AREA* is an area name (see **AREAS** section for more details).

The *puppet-hpc/* directory is a checkout of Puppet-HPC.

The *private-data/* directory contains all the specific data for every clusters
of your organization. Please refer to Puppet-HPC reference documentation for
more details about the files hierarchy of this directory. It's advised to also
keep this in git and simply fetch a copy.

The destination should be shared between all the central storage servers. It
must be accessible as a simple POSIX file system, via the Amazon S3 API or a
set of SFTP servers.

# AREAS

*hpc-config-push* supports splitting cluster configuration environments into
multiple areas for security purpose. Each area has its own set of encryption
keys. Please refer to Puppet-HPC reference documentation for more details on
this mechanism.

If multiple areas are declared into its configuration file, *hpc-config-push*
considers the first area to be the **main** area. As a requirement, all the
encrypted files located into the *private-data/files/\$CLUSTER* directory must be
encrypted with the cluster **main** area files encryption key, and all the eyaml
encrypted parameters in the *private-data/hieradata/\$CLUSTER/areas* file must be
encrypted with the cluster **main** area eyaml encryption key.

When the configuration environment is pushed, *hpc-config-push* performs
on-the-fly re-encryption of area's sensitive data using area specific
encryption keys. It includes the encrypted files (\*.enc) located in the
*cluster* and the *\$AREA* subdirectories and the eyaml encrypted parameters in
the *\$CLUSTER/areas/\$AREA.yaml* file.

Then, *hpc-config-push* generates a subset of the configuration environment for
each area, excluding the sensitive data of all other areas.

This way, each area only has access to its own sensitive data encrypted with
its own set of encryption keys.

By default, *hpc-config-push* considers there is only one **default** area, and
no re-encryption is performed.

# CONFIGURATION FILE

The default configuration file is installed at `/etc/hpc-config/push.conf` and
it is a simple text file using the
[INI file format](http://en.wikipedia.org/wiki/INI_file).
This file has a basic structure composed of sections, properties, and values.

The '[global]' section defines the defaults parameters used:

    [global]
    cluster = <cluster name>
    environment = <default environment>
    version = <default version>
    areas = <list of cluster areas>
    destination = <default directory on central storage>
    mode = <push mode, can be 's3', 'posix' or 'sftp'>

Optionally, it can include a '[posix]' section:

    [posix]
    file_mode = <dest files mode as (octal)>
    dir_mode = <dest directories mode (octal)>

Or a '[s3]' section:

    [s3]
    access_key = <access key for s3>
    secret_key = <secret key for s3>
    bucket_name = <bucket to use on s3>
    host = <host where to push data>
    port = <port to use>

Or a '[sftp]' section:

    [sftp]
    hosts = <host>[,<host>...]
    username = <SSH username>
    private_key = <Private key file path>

And/or a '[paths]' section:

    [paths]
    tmp = <tmp directory where to build the tarball> (default: /tmp/hpc-config-push)
    puppethpc = <directory where to find the puppet-hpc git repository>
                (default: puppet-hpc)
    privatedata = <directory where to find the private data>
                  (default: hpc-privatedata)
    puppet_conf = <directory where to find puppet.conf file>
                  (default: ${privatedata}/puppet-config/${global:cluster}/puppet.conf)
    hiera_conf = <directory where to find the puppet.conf file> (default:
                 ${privatedata}/puppet-config/${global:cluster}/hiera.yaml)
    nodes_private = ${privatedata}/puppet-config/${global:cluster}/cluster-nodes.yaml
    modules_generic = <directories where to find the generic puppet modules>
                      (default: ${puppethpc}/puppet-config/cluster,
                       ${puppethpc}/puppet-config/modules,
                       /usr/share/puppet/modules )
    modules_private = <directories where to find the private puppet modules>
                      (default: ${privatedata}/puppet-config/${global:cluster}/modules)
    manifests_generic = <directory where to find the generic manifests>
                        (default: ${puppethpc}/puppet-config/manifests)
    manifests_private = <directory where to find the private manifests>
                        (default: ${privatedata}/puppet-config/${global:cluster}/manifests)
    hieradata_generic = <directory where to find the generic Hiera files>
                        (default: ${puppethpc}/hieradata)
    hieradata_private = <directory where to find the private Hiera files>
                        (default: ${privatedata}/hieradata)
    files_private = <directory where to find all the private files to put on nodes>
                    (default: ${privatedata}/files/${global:cluster})

All the values in the '[paths]' section are optional, if they are not defined,
the default value is used.

# EXAMPLES

To simply push the current configuration in the default environment:

    hpc-config-push

To push the current configuration in the 'test' environment:

    hpc-config-push -e test

# SEE ALSO

hpc-config-apply(1)
