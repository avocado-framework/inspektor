Summary: Inspektor python project checker
Name: inspektor
Version: 0.1.5
Release: 1%{?dist}
License: GPLv2
Group: Development/Tools
URL: https://github.com/lmr/inspektor
Source: inspektor-%{version}.tar.gz
BuildRequires: python2-devel
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
%{_datadir}/inspektor

%changelog
* Thu Apr 10 2014 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.5-1
- Created initial spec file
