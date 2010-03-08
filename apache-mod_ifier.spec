#Module-Specific definitions
%define mod_name mod_ifier
%define mod_conf A66_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Request filtering and rejection module for Apache2
Name:		apache-%{mod_name}
Version:	0.8
Release:	%mkrel 8
Group:		System/Servers
License:	GPL
URL:		http://www.steve.org.uk/Software/mod_ifier/
Source0:	http://www.steve.org.uk/Software/mod_ifier/mod-ifier-%{version}.tar.bz2
Source1:	%{mod_conf}
Patch0:		mod-ifier-0.4-no_apr_compat.diff
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.0.54
Requires(pre):	apache >= 2.0.54
Requires:	apache-conf >= 2.0.54
Requires:	apache >= 2.0.54
BuildRequires:  apache-devel >= 2.0.54
BuildRequires:	file
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
This is a simple Apache 2.x module which is designed to stand in front of
requests to an Apache server, and either deny or filter incoming requests.

So far only the "deny" options are setup, and the module allows you to send a
403 (access denied) as a result of matches made against arbitary incoming HTTP
headers.

The intention is to filter out broken, malicious, or otherwise bogus requests
before they are handled by Apache - in a similar manner to mod_security.

%prep

%setup -q -n mod-ifier-%{version}
%patch0 -p0

find . -type d -perm 0700 -exec chmod 755 {} \;
find . -type d -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0555 -exec chmod 755 {} \;
find . -type f -perm 0444 -exec chmod 644 {} \;

for i in `find . -type d -name CVS` `find . -type d -name .svn` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -r $i; fi >&/dev/null
done

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

cp %{SOURCE1} %{mod_conf}

%build

pushd src
    %{_sbindir}/apxs -DVERSION='\"%{version}\"' -c %{mod_name}.c
popd

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}%{_libdir}/apache-extramodules

install -m0755 src/.libs/%{mod_so} %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post
if [ -f /var/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f /var/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc README docs/example.conf docs/AUTHORS
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
