Name:		pptp
Version:	1.7.2
Release:	20%{?dist}
Summary:	Point-to-Point Tunneling Protocol (PPTP) Client
Group:		Applications/Internet
License:	GPLv2+
URL:		http://pptpclient.sourceforge.net/
Source0:	http://downloads.sf.net/pptpclient/pptp-%{version}.tar.gz
Source1:	pptp-tmpfs.conf
Patch0:		pptp-1.7.2-compat.patch
Patch1:		pptp-1.7.2-ip-path.patch
Patch2:		pptp-1.7.2-pptpsetup.patch
Patch3:		pptp-1.7.2-makedeps.patch
Patch4:		pptp-1.7.2-pptpsetup-encrypt.patch
Patch5:		pptp-1.7.2-pptpsetup-mppe.patch
Patch6:		pptp-1.7.2-waitpid.patch
Patch7:		pptp-1.7.2-conn-free.patch
Patch8:		pptp-1.7.2-conn-free2.patch
Patch9:		pptp-1.7.2-call-disconnect-notify.patch
Patch10:	pptp-1.7.2-so_mark.patch
Patch11:	pptp-1.7.2-nohostroute-option.patch
Patch12:	pptp-1.7.2-parallel-build.patch
Patch13:	pptp-1.7.2-fsf-update.patch
Patch14:	pptp-1.7.2-sign-compare.patch
Patch15:	pptp-1.7.2-const.patch
Patch16:	pptp-1.7.2-field-init.patch
Patch17:	pptp-1.7.2-unused.patch
Patch18:	pptp-1.7.2-prototype.patch
Patch19:	pptp-1.7.2-nested-externs.patch
Patch20:	pptp-1.7.2-aliasing.patch
Patch21:	pptp-1.7.2-options.pptp.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(id -nu)
BuildRequires:	/usr/bin/pod2man
Requires:	ppp >= 2.4.2, /sbin/ip
%if 0%{?fedora} > 14
Requires:	systemd-units
%endif

%description
Client for the proprietary Microsoft Point-to-Point Tunneling
Protocol, PPTP. Allows connection to a PPTP based VPN as used
by employers and some cable and ADSL service providers.

%package setup
Summary:	PPTP Tunnel Configuration Script
Group:		Applications/Internet
Requires:	%{name} = %{version}-%{release}

%description setup
This package provides a simple configuration script for setting up PPTP
tunnels.

%prep
%setup -q

# Remove reference to stropts.h, not shipped in F9 onwards (applied upstream)
%patch0 -p0 -b .compat

# Make location of "ip" binary build-time configurable (applied upstream)
%patch1 -p0 -b .ip-path

# Retain permissions on /etc/ppp/chap-secrets (#492090, applied upstream)
%patch2 -p0 -b .bz492090

# Fix Makefile dependencies to support parallel make (applied upstream)
%patch3 -p0 -b .makedeps
%patch12 -p0 -b .parallel

# Don't check for MPPE capability in kernel or pppd unless we're creating a
# tunnel that requires encryption (applied upstream)
%patch4 -p0 -b .encrypt

# Don't check for MPPE capability in kernel and pppd at all because current
# Fedora releases and EL ≥ 5 include MPPE support out of the box (#502967)
%patch5 -p1 -b .mppe

# Fix waitpid usage (upstream patch)
%patch6 -p0 -b .waitpid

# Move free of connection struct out of main loop (upstream patch)
%patch7 -p0 -b .conn-free

# Avoid using connection struct after it is freed (upstream patch)
%patch8 -p0 -b .conn-free2

# Add call ID of outgoing call so that Call-Disconnect-Notify from peer causes
# correct disconnection sequence (upstream patch)
%patch9 -p1 -b .cdn

# Add support for setting SO_MARK for the PPTP TCP control connection as well
# as on the GRE packets (upstream patch)
%patch10 -p1 -b .so_mark

# Implement the --nohostroute option that routing.c talks about (upstream patch)
%patch11 -p1 -b .nohostroute

# Update the FSF address references and GPLv2 license text (upstream patch)
%patch13 -p0 -b .fsf

# Fix comparisons between signed and unsigned integers (upstream patch)
%patch14 -p1 -b .sign-compare

# Fix const usage (upstream patch)
%patch15 -p1 -b .const

# Add missing field initializers (upstream patch)
%patch16 -p1 -b .field

# Suppress warnings about possibly unused variables (upstream patch)
%patch17 -p1 -b .unused

# Fix declarations that are not prototypes (upstream patch)
%patch18 -p1 -b .prototype

# Fix warnings about nested externs (upstream patch)
%patch19 -p1 -b .nested

# Fix aliasing issues (upstream patch)
%patch20 -p1 -b .alias

# Additional commentary in options.pptp regarding encryption (upstream patch)
%patch21 -b .options-comments

# Pacify rpmlint
perl -pi -e 's/install -o root -m 555 pptp/install -m 755 pptp/;' Makefile

%build
OUR_CFLAGS="-Wall %{optflags} -Wextra -Wstrict-aliasing=2 -Wnested-externs -Wstrict-prototypes"
make %{?_smp_mflags} CFLAGS="$OUR_CFLAGS" IP=/sbin/ip

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install
install -d -m 750 %{buildroot}%{_localstatedir}/run/pptp

# Make sure /var/run/pptp exists at boot time for systems
# with /var/run on tmpfs (#656672)
%if 0%{?fedora} > 14
install -d -m 755 %{buildroot}%{_prefix}/lib/tmpfiles.d
install -p -m 644 %{SOURCE1} %{buildroot}%{_prefix}/lib/tmpfiles.d/pptp.conf
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING DEVELOPERS NEWS README TODO USING
%doc ChangeLog Documentation/DESIGN.PPTP PROTOCOL-SECURITY
%if 0%{?fedora} > 14
%{_prefix}/lib/tmpfiles.d/pptp.conf
%endif
%{_sbindir}/pptp
%{_mandir}/man8/pptp.8*
%dir %attr(750,root,root) %{_localstatedir}/run/pptp/
%config(noreplace) %{_sysconfdir}/ppp/options.pptp

%files setup
%defattr(-,root,root,-)
%{_sbindir}/pptpsetup
%{_mandir}/man8/pptpsetup.8*

%changelog
* Thu Feb 14 2013 Paul Howarth <paul@city-fan.org> 1.7.2-20.0.cf
- BR: /usr/bin/pod2man for generation of pptpsetup man page

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.2-19
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Tue Nov 27 2012 Paul Howarth <paul@city-fan.org> 1.7.2-18
- Don't hard-code /etc (#880574)

* Fri Aug 31 2012 Paul Howarth <paul@city-fan.org> 1.7.2-17
- Add note in options.pptp about MPPE not being available in FIPS mode
  (#845112)
- Add note in options.pptp about PPTP with MSCHAP-V2 being insecure

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> 1.7.2-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jul  4 2012 Paul Howarth <paul@city-fan.org> 1.7.2-15
- Move tmpfiles.d config from %%{_sysconfdir} to %%{_prefix}/lib

* Wed Jan  4 2012 Paul Howarth <paul@city-fan.org> 1.7.2-14
- Build with warning-fix patches to address occasional segfaults (#749455)
- Patches have all now been merged upstream

* Wed Nov 30 2011 Paul Howarth <paul@city-fan.org> 1.7.2-13.2
- Add patch to fix highly-parallel build (e.g. -j16)
- Add additional compiler warning flags to highlight questionable code
- Add patch to fix comparisons between signed and unsigned integers
- Add patch to fix const usage
- Add patch to fix missing field initializers
- Add patch to suppress warnings about possibly unused variables
- Add patch to fix declarations that are not prototypes
- Add patch to fix warnings about nested externs
- Add patch to fix dubious typecasts that violate strict-aliasing rules
- Update the FSF address references and GPLv2 license text
- Use default optimization level (-O2) again

* Fri Nov 11 2011 Paul Howarth <paul@city-fan.org> 1.7.2-13.1
- Drop compiler optimization level to -O0 as per upstream in attempt to
  resolve occasional segfault in pptpcm (#749455)
- Add patch to fix highly-parallel build (e.g. -j16)

* Tue Nov  8 2011 Paul Howarth <paul@city-fan.org> 1.7.2-13
- Patch to fix broken Call-Disconnect-Notify code accepted upstream
- Add upstream patch to support setting SO_MARK for the PPTP TCP control
  connection as well as on the GRE packets
- Add upstream patch to implement the --nohostroute option
- Nobody else likes macros for commands

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> 1.7.2-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Nov 30 2010 Paul Howarth <paul@city-fan.org> 1.7.2-11
- Require systemd-units for ownership of /etc/tmpfiles.d directory
- Fix Call-Disconnect-Notify operation

* Thu Nov 25 2010 Paul Howarth <paul@city-fan.org> 1.7.2-10
- Add /etc/tmpfiles.d/pptp.conf to create /var/run/pptp at boot time for
  systems with /var/run on tmpfs (#656672)

* Wed Jun 16 2010 Paul Howarth <paul@city-fan.org> 1.7.2-9
- Add some fixes from CVS:
  - Fix waitpid usage
  - Move free of connection struct out of main loop
  - Avoid using connection struct after it is freed

* Thu Sep 24 2009 Paul Howarth <paul@city-fan.org> 1.7.2-8
- Split pptpsetup into subpackage to avoid perl dependency (#524972)

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.2-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jun  1 2009 Paul Howarth <paul@city-fan.org> 1.7.2-6
- Don't check for MPPE capability in kernel and pppd unless we're creating a
  tunnel that requires encryption
- Don't check for MPPE capability in kernel and pppd at all because current
  Fedora releases and EL >= 5 include MPPE support out of the box (#502967)

* Wed Mar 25 2009 Paul Howarth <paul@city-fan.org> 1.7.2-5
- Retain permissions on /etc/ppp/chap-secrets when using pptpsetup (#492090)
- Use upstream versions of patches
- Re-enable parallel build; Makefile dependencies now fixed
- Use perl rather than sed to edit Makefile, for spec compatibility with
  ancient distro releases

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon May 19 2008 Paul Howarth <paul@city-fan.org> 1.7.2-3
- Add dependency on /sbin/ip
- Disable parallel make - object files are missing dependency on config.h

* Mon May 19 2008 Paul Howarth <paul@city-fan.org> 1.7.2-2
- Use /sbin/ip, not /bin/ip for routing

* Wed May 14 2008 Paul Howarth <paul@city-fan.org> 1.7.2-1
- Update to 1.7.2
- New script and manpage: pptpsetup
- Add patch to remove reference to stropts.h, not shipped in F9 onwards

* Wed Feb 13 2008 Paul Howarth <paul@city-fan.org> 1.7.1-4
- Rebuild with gcc 4.3.0 for Fedora 9

* Fri Aug 24 2007 Paul Howarth <paul@city-fan.org> 1.7.1-3
- Change download URL from df.sf.net to downloads.sf.net
- Expand tabs in spec
- Clarify license as GPL version 2 or later

* Wed Aug 30 2006 Paul Howarth <paul@city-fan.org> 1.7.1-2
- FE6 mass rebuild

* Mon Feb 13 2006 Paul Howarth <paul@city-fan.org> 1.7.1-1
- new upstream version 1.7.1 (fixes #166394)
- include new document PROTOCOL-SECURITY
- cosmetic change: replace variables with macros

* Wed Aug 10 2005 Paul Howarth <paul@city-fan.org> 1.7.0-2
- own directory %%{_localstatedir}/run/pptp

* Thu Jul 28 2005 Paul Howarth <paul@city-fan.org> 1.7.0-1
- new upstream version 1.7.0
- remove patch, included upstream
- edit Makefile to prevent attempted chown in %%install
- remove redundant %%attr tag in %%files
- honour $RPM_OPT_FLAGS
- ensure directories have correct permissions

* Fri May 27 2005 Paul Howarth <paul@city-fan.org> 1.6.0-5
- bump and rebuild

* Tue May 17 2005 Paul Howarth <paul@city-fan.org> 1.6.0-4
- rebuild with dist tags

* Tue May 10 2005 Paul Howarth <paul@city-fan.org> 1.6.0-3
- fix URL for SOURCE0 not to point to a specific sf.net mirror

* Tue May 10 2005 Paul Howarth <paul@city-fan.org> 1.6.0-2
- Weed out documentation useful only to developers
- Add dist tag
- Use full URL for SOURCE0
- Fix permissions on %%{_sbindir}/pptp

* Fri May  6 2005 Paul Howarth <paul@city-fan.org> 1.6.0-1
- First build for Fedora Extras, based on upstream spec file
