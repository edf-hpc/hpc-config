%{!?__unit_dir:%global __unit_dir /etc/systemd/system}
%{!?__lib_dir:%global __lib_dir /usr/lib}

Name:		hpc-config
Version:	3.1.1
Release:	3%{?dist}.edf
License:	GPLv2+
Summary:	Suite of utilities to deploy HPC clusters generic configuration
URL:		https://github.com/scibian/hpc-config
Source0:	%{name}-%{version}.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildRequires: python3, python3-pyyaml, python3-urllib3, python3-paramiko, python3-GitPython, rubygem-hiera-eyaml

%global debug_package %{nil}

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
%{__python3} setup.py build

%install
#rm -rf %{buildroot} # for git
#cd %{name}-%{version} # for git
install -m 755 -d %{buildroot}%{_sbindir}
install -m 755 -d %{buildroot}%{__unit_dir}
install -m 755 -d %{buildroot}%{_sysconfdir}/%{name}
install -m 755 init/systemd/%{name}-apply.service %{buildroot}%{__unit_dir}
install -m 755 README.md CHANGELOG.md %{_builddir}
install -m 755 -d %{buildroot}%{_mandir}
install -D -m 755 -t %{buildroot}%{_mandir}/man1 doc/manpages/%{name}-*.1
install -m 755 -d %{buildroot}%{__lib_dir}/%{name}/exec
install -m 755 hpcconfig/cluster-node-classifier %{buildroot}%{__lib_dir}/%{name}/exec
%{__python3} setup.py install --install-scripts=%{_sbindir} --root %{buildroot}

%clean
rm -rf %{buildroot}

%package common
Summary: %{name} library
Requires: python3, python3-pyyaml, python3-urllib3, python3-paramiko

%description common
This package provide the hpc-config library required by hpc-config-apply
and hpc-config-push tools.

%files common
%doc README.md CHANGELOG.md
%{python3_sitelib}/*

%package apply
Summary: %{name}-apply script to deploy the configuration on a node
Requires: %{name}-common python3-clustershell clustershell
Obsoletes: %{name}-apply <= 3.0
Provides: %{name}-apply = %{version}

%description apply
This package provide the hpc-config-apply script necessary to deploy the
configuration on a RHEL node.
It also provide a service file that applies it during the boot sequence.

%files apply
%defattr(-,root,root,-)
%{_sbindir}/hpc-config-apply
%{__unit_dir}/%{name}-apply.service
%{_sysconfdir}/%{name}
%{_mandir}/man1/%{name}-apply.1.gz
%{__lib_dir}/hpc-config/exec/cluster-node-classifier


%package push
Summary: %{name}-push script to deploy the configuration on a node
Requires: %{name}-common python3-GitPython, rubygem-hiera-eyaml
Obsoletes: %{name}-push <= 3.0
Provides: %{name}-push = %{version}

%description push
This package provide the hpc-config-push script to push the configuration
on a central location or a set of servers.

%files push
%defattr(-,root,root,-)
%{_sbindir}/hpc-config-push
%{_mandir}/man1/%{name}-push.1.gz

%changelog

* Thu Apr 14 2022 Kwame Amedodji <kwame-externe.amedodji@edf.fr> - 3.1.1-3el8.edf
- New upstream release 3.1.1-3
- make obsolete previous < 3.0 version
- add dep on python3-clustershell and clustershell

* Wed Mar 23 2022 Kwame Amedodji <kwame-externe.amedodji@edf.fr> - 3.1.1-1el8.edf
- New upstream release 3.1.1

* Tue Jan 25 2022 Rémi Palancher <remi-externe.palancher@edf.fr> - 3.1.0-1el8.edf
- New upstream release 3.1.0
- Fix bogus date in changelog
- Introduce -common package for python library shared by both -apply and -push
- Adopt setup.py to install python module
- Fix man pages installation path

* Tue Jan 11 2022 Kwame Amedodji <kwame-externe.amedodji@edf.fr> - 3.0.4
- New release 3.0.4
- revert support of python setuptools
- enforce python36
- add version to uncompress package name dir

* Sat Jan 01 2022 Kwame Amedodji <kwame-externe.amedodji@edf.fr> - 3.0.3
- New release 3.0.3
- c-n-classifier: support explicit given role name
- h-c-apply: variabilized rhel vs debian puppet paths

* Fri Oct 30 2020 Guillaume RANQUET <guillaume-externe.ranquet@edf.fr> - 3.0.2
- New release 3.0.2
- Use python setuptools to build/install

* Tue Oct 20 2020 Nilce BOUSSAMBA <nilce-externe.boussamba@edf.fr> - 3.0.1
- New release 3.0.1
- modify node-classifier to handle multiple areas

* Mon Sep 21 2020 Thomas HAMEL <thomas-t.hamel@edf.fr> - 3.0.0
- New release 3.0.0
- include node-classifier

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
