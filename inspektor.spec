%global inspektorversion 0.5.2
Summary: Inspektor python project checker
Name: inspektor
Version: %{inspektorversion}
Release: 0%{?dist}
License: GPLv2
Group: Development/Tools
URL: https://github.com/avocado-framework/inspektor
Source: inspektor-%{inspektorversion}.tar.gz
BuildArch: noarch

%if "%{?dist}" == ".el6"
Requires: python, pylint < 1.4, python-pep8, python-logutils, python-six, python-cliff
BuildRequires: python2-devel, pylint < 1.4, python-pep8, python-logutils, python-six, python-cliff
%else
Requires: python, pylint >= 1.3, python-pep8, python-logutils, python-six, python-cliff
BuildRequires: python2-devel, pylint >= 1.3, python-pep8, python-six, python-cliff
%endif

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
* Wed Jul 18 2018 Lucas Meneghel Rodrigues <lookkas@gmail.com> - 0.5.2-0
- New upstream version 0.5.2
* Thu May  3 2018 Cleber Rosa <cleber@redhat.com> - 0.5.1-0
- New upstream version 0.5.1
* Thu May  3 2018 Cleber Rosa <cleber@redhat.com> - 0.4.6-0
- New upstream version 0.4.6
- Updated URL from autotest to avocado-framework project
* Fri Aug 11 2017 Lucas Meneghel Rodrigues <lookkas@gmail.com> - 0.4.5-0
- New upstream version 0.4.5
* Wed Jul 19 2017 Lucas Meneghel Rodrigues <lookkas@gmail.com> - 0.4.0-0
- New upstream version 0.4.0
- Application is now based on the cliff python app framework
* Fri May 5 2017 Lucas Meneghel Rodrigues <lookkas@gmail.com> - 0.3.0-0
- New upstream version 0.3.0
* Mon Jan 18 2016 Lucas Meneghel Rodrigues <lookkas@gmail.com> - 0.2.1-0
- New upstream version 0.2.1
* Tue Dec 2 2015 Lucas Meneghel Rodrigues <lookkas@gmail.com> - 0.2.0-0
- New upstream version 0.2.0
* Thu Mar 19 2015 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.15-3
- Add conditional build dependencies
* Wed Mar 11 2015 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.15-2
- Fix build on COPR
* Wed Mar 11 2015 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.15-1
- New upstream version 0.1.15
* Tue Apr 29 2014 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.9-5
- Moved macro definitions to rpm spec file, fix build on COPR
* Tue Apr 29 2014 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.9-4
- Fix error in pkg spec that was preventing build on COPR
* Tue Apr 29 2014 Lucas Meneghel Rodrigues <lmr@redhat.com> - 0.1.9-3
- Fix error in pkg spec that was preventing build on COPR
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
