Summary: Inspektor python project checker
Name: inspektor
Version: %{inspektorversion}
Release: 2%{?dist}
License: GPLv2
Group: Development/Tools
URL: https://github.com/lmr/inspektor
Source: inspektor-%{inspektorversion}.tar.gz
BuildRequires: python2-devel
BuildRequires: pylint > 1.0
BuildRequires: python-autopep8
BuildArch: noarch
Requires: python, python-autopep8, pylint > 1.0

%description
Inspektor is a checker tool, that tries to automate a number of checks in a
python project code:
* Syntax
* Indentation
* PEP8 compliance
It also helps you to batch add license header files, and analyze github pull
requests, in case your project uses github. Inspektor was developed to ease
patch review for programs developed by the autotest project team.

%prep
%setup -q

%build
%{__python} setup.py build

%install
%{__python} setup.py install --root %{buildroot} --skip-build

%files
%defattr(-,root,root,-)
%doc README.rst LICENSE
%{_bindir}/inspekt
%{python_sitelib}/inspektor*


%changelog
* Tue Apr 29 2014 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.9-2
- Fix error in pkg spec that was preventing build on COPR
* Tue Apr 29 2014 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.9-1
- New upstream version
* Thu Apr 10 2014 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.5-3
- Fix autopep8 build dep
* Thu Apr 10 2014 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.5-2
- Fix pylint build dep
* Thu Apr 10 2014 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.5-1
- Created initial spec file
