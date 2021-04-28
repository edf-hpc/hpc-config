%{!?__unit_dir:%global __unit_dir /etc/systemd/system}
%{!?__lib_dir:%global __lib_dir /usr/lib}

Name:		hpc-config
Version:	2.0.5
Release:	2%{?dist}
License:	GPLv2+
Summary:	Suite of utilities to deploy HPC clusters generic configuration
URL:		https://github.com/scibian/hpc-config
Source0:	%{name}-%{version}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

%description
hpc-config is a suite of utilities to ease deployment of Puppet-HPC, a
Puppet-based software stack designed to easily deploy HPC clusters. The main
goal of Puppet-HPC is to provide a common generic configuration management
system that can be used effortlessly across multiple HPC clusters and
organizations.

%prep
#[ -f %{_sourcedir}/%{name}-%{version}.tar.gz ] &&
%setup -q
##|| {
#    [ -d %{name}-%{version} ] || git clone %{url}.git %{name}-%{version}
#    cd %{name}-%{version} # for git
##}

%build

%install
#rm -rf %{buildroot} # for git
#cd %{name}-%{version} # for git
install -m 755 -d %{buildroot}%{_sbindir}
install -m 755 scripts/%{name}-* %{buildroot}%{_sbindir}
install -m 755 -d %{buildroot}%{__unit_dir}
install -m 755 -d %{buildroot}%{_sysconfdir}/%{name}
install -m 755 init/systemd/%{name}-apply.service %{buildroot}%{__unit_dir}
install -m 755 README.md CHANGELOG.md %{_builddir}
install -m 755 -d %{buildroot}%{_mandir}
install -m 755 doc/manpages/%{name}-*.1 %{buildroot}%{_mandir}
install -m 755 -d %{buildroot}%{__lib_dir}/%{name}/exec
#install -m 755 scripts/cluster-node-classifier %{buildroot}%{__lib_dir}/%{name}/exec

%clean
rm -rf %{buildroot}

%package apply
Summary: %{name}-apply script to deploy the configuration on a node
Requires: python36, python36-PyYAML, python36-urllib3

%description apply
This package provide the hpc-config-apply script necessary to deploy the
configuration on a RHEL node.
It also provide a service file that applies it during the boot sequence.

%files apply
%defattr(-,root,root,-)
%doc README.md CHANGELOG.md
%{_sbindir}/hpc-config-apply
%{__unit_dir}/%{name}-apply.service
%{_sysconfdir}/%{name}
%{_mandir}/%{name}-apply.1
#%{__lib_dir}/hpc-config/exec/cluster-node-classifier


%package push
Summary: %{name}-apply script to deploy the configuration on a node
Requires: python36, python36-PyYAML, python36-urllib3

%description push
This package provide the hpc-config-push script to push the configuration
on a central location or a set of servers.

%files push
%defattr(-,root,root,-)
%doc README.md CHANGELOG.md
%{_sbindir}/hpc-config-push
%{_mandir}

%changelog

* Tue Jan 14 2020 Kwame Amedodji <kwame-externe.amedodji@edf.fr> - 2.0.5
- New release 2.0.5
- RPM release base on latest debian one

* Tue Jan 16 2018 Thomas Hamel <thomas-externe.hamel@edf.fr> - 1.1.6
- New release 1.1.6
- Optimize hpc-config-push

* Thu Aug 17 2017 Thomas Hamel <thomas-externe.hamel@edf.fr> - 1.1.4
- New release 1.1.4

* Tue Aug 08 2017 Thomas Hamel <thomas-externe.hamel@edf.fr> - 1.1.3
- New release 1.1.3

* Tue Aug 08 2017 Thomas Hamel <thomas-externe.hamel@edf.fr> - 1.1.2
- New release 1.1.2

* Tue May 30 2017 Thomas Hamel <thomas-externe.hamel@edf.fr> - 1.1.0
- Initial release 1.1.0
