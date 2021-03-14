%global packdname -%{version}

%global _hardened_build 1

Name:          android-tools
Version:       30.0.5p1
Release:       1%{?dist}
Summary:       Android platform tools(adb, fastboot)

# The entire source code is ASL 2.0 except boringssl which is BSD
License:       ASL 2.0 and (ASL 2.0 and BSD)
URL:           http://developer.android.com/guide/developing/tools/

#  Sources with all needed patches and cmakelists live there now: 
#  
Source0:       https://github.com/nmeum/%{name}/releases/download/%{version}/%{name}-%{version}.tar.xz
Source1:       51-android.rules
Source2:       adb.service


Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
BuildRequires: cmake
BuildRequires: gtest-devel
BuildRequires: libusbx-devel
BuildRequires: systemd

Provides:      adb = %{epoch}:%{version}-%{release}
Provides:      fastboot = %{epoch}:%{version}-%{release}
Provides:      mke2fs.android = %{epoch}:%{version}-%{release}

# Bundled bits
Provides: bundled(boringssl)

%description

The Android Debug Bridge (ADB) is used to:

- keep track of all Android devices and emulators instances
  connected to or running on a given host developer machine

- implement various control commands (e.g. "adb shell", "adb pull", etc.)
  for the benefit of clients (command-line users, or helper programs like
  DDMS). These commands are what is called a 'service' in ADB.

Fastboot is used to manipulate the flash partitions of the Android phone. 
It can also boot the phone using a kernel image or root filesystem image 
which reside on the host machine rather than in the phone flash. 
In order to use it, it is important to understand the flash partition 
layout for the phone.
The fastboot program works in conjunction with firmware on the phone 
to read and write the flash partitions. It needs the same USB device 
setup between the host and the target phone as adb.

%prep
%autosetup
cp -p %{SOURCE1} 51-android.rules
 

%build
%cmake -DBUILD_SHARED_LIBS:BOOL=OFF
%cmake_build

%install
%cmake_install
install -p -D -m 0644 %{SOURCE2} \
    %{buildroot}%{_unitdir}/adb.service
install -d -m 0775 ${RPM_BUILD_ROOT}%{_sharedstatedir}/adb

%post
%systemd_post adb.service

%preun
%systemd_preun adb.service

%postun
%systemd_postun_with_restart adb.service

%files
%doc vendor/core/adb/OVERVIEW.TXT vendor/core/adb/SERVICES.TXT vendor/core/adb/NOTICE vendor/core/adb/protocol.txt 51-android.rules
%{_unitdir}/adb.service
%attr(0755,root,root) %dir %{_sharedstatedir}/adb
#ASL2.0 and BSD
%{_bindir}/adb
#ASL2.0
%{_bindir}/simg2img
%{_bindir}/img2simg
%{_bindir}/fastboot
%{_bindir}/append2simg
%{_bindir}/mke2fs.android


%changelog
* Sun Mar 14 2021 Ivan Afonichev <ivan.afonichev@gmail.com> - 1:30.0.5p1-1
- Switch to linux-friendly upstream
- Use Android SDK versions for versioning(Epoch 1 introduced)
- Resolves: rhbz 1937578 1873878 1923681 1776001

* Tue Mar 02 2021 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 20180828gitc7815d675-11
- Rebuilt for updated systemd-rpm-macros
  See https://pagure.io/fesco/issue/2583.

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 20180828gitc7815d675-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Fri Nov 6 2020 Ivan Afonichev <ivan.afonichev@gmail.com> - 20180828gitc7815d675-9
- Fix plugdev udev rule 
- Resolves: rhbz 1779855

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 20180828gitc7815d675-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Mon Jul 20 2020 Jeff Law <law@redhat.com> - 20180828gitc7815d675-7
- Move LTO disablement so that it impacts the optflags override too

* Sat Jul 11 2020 Jeff Law <law@redhat.com> - 20180828gitc7815d675-6
- Disable LTO

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 20180828gitc7815d675-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 20180828gitc7815d675-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Mon May 27 2019 Peter Robinson <pbrobinson@fedoraproject.org> 20180828gitc7815d675-3
- Fix FTBFS, minor cleanups

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 20180828gitc7815d675-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Wed Aug 29 2018 Ivan Afonichev <ivan.afonichev@gmail.com> - 20180828gitc7815d675-1
- Update to upstream git commit c7815d675
- Resolves: rhbz 1535542 1550703 1603379 Switch to clang and ninja

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 20170311gite7195be7725a-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Feb 27 2018 Bastien Nocera <bnocera@redhat.com> - 20170311gite7195be7725a-7
- Fix USB resets when adb daemon is started (#1470740)

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 20170311gite7195be7725a-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Oct 26 2017 Vít Ondruch <vondruch@redhat.com> - 20170311gite7195be7725a-5
- Drop the explicit dependnecy on rubypick.

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 20170311gite7195be7725a-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 20170311gite7195be7725a-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Apr 25 2017 Jan Pokorný <jpokorny@fedoraproject.org> - 20170311gite7195be7725a-2
- Resolves: rhbz 1441234 Fix adb crash when generating a key (OpenSSL 1.1.0 API)

* Sat Mar 11 2017 Ivan Afonichev <ivan.afonichev@gmail.com> - 20170311gite7195be7725a-1
- Update to upstream git commit e7195be7725a
- Resolves: rhbz 1323632 1423219 Add optflags. Support new versions.

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 20160327git3761365735de-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sun May 08 2016 Bastien Nocera <hadess@hadess.net> - 20160327git3761365735de-2
- Add missing BuildRequires for Ruby script to run
- Compile and build img2simg and simg2img

* Mon Apr  4 2016 Ville Skyttä <ville.skytta@iki.fi> - 20160327git3761365735de-2
- Build with %%{optflags}

* Sun Mar 27 2016 Ivan Afonichev <ivan.afonichev@gmail.com> - 20160327git3761365735de-1
- Update to upstream git commit 3761365735de

* Sat Mar 26 2016 Ivan Afonichev <ivan.afonichev@gmail.com> - 20160321git922e151ba2d8-1
- Update to upstream git commit 922e151ba2d8
- Resolves: rhbz 1278769 1318099 Migrate to ruby generate_build. Support new versions 

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 20141219git8393e50-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Jun 16 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 20141219git8393e50-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed May 20 2015 Bastien Nocera <bnocera@redhat.com> 20141224git8393e50-3
- Remove Apple from the vendor to launch adb.service for
  They never created an Android phone, and probably never will

* Sun Jan 11 2015 Ivan Afonichev <ivan.afonichev@gmail.com> - 20141224git8393e50-2
- Resolves: rhbz 1062095 Harden android-tools
- Remove 0002-Add-missing-headers.patch

* Wed Dec 24 2014 Jonathan Dieter <jdieter@lesbg.com> - 20141224git8393e50-1
- Update to 5.0.2 release

* Fri Sep 19 2014 Ivan Afonichev <ivan.afonichev@gmail.com> - 20130123git98d0789-5
- Added more udev devices
- Resolves: rhbz 967216 Adb service now stores keys in /var/lib/adb

* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 20130123git98d0789-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 20130123git98d0789-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 20130123git98d0789-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jan 28 2013 Ivan Afonichev <ivan.afonichev@gmail.com> - 20130123git98d0789-1
- Update to upstream git commit 98d0789
- Resolves: rhbz 903074 Move udev rule to docs as example
- Resolves: rhbz 879585 Introduce adb.service with PrivateTmp

* Tue Nov 20 2012 Ivan Afonichev <ivan.afonichev@gmail.com> - 20121120git3ddc005-1
- Update to upstream git commit 3ddc005
- Added more udev devices
- Added ext4_utils from extras for fastboot
- Updated makefiles
- Resolves: rhbz 869624 start adb server by udev

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 20120510gitd98c87c-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu May 10 2012 Ivan Afonichev <ivan.afonichev@gmail.com> - 20120510gitd98c87c-1
- Update to upstream git commit d98c87c
- Added more udev devices
- Resolves: rhbz 819292 secure udev permissions

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 20111220git1b251bd-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Dec 20 2011 Ivan Afonichev <ivan.afonichev@gmail.com> - 20111220git1b251bd-1
- Update to upstream git commit 1b251bd

* Wed Nov 23 2011 Ivan Afonichev <ivan.afonichev@gmail.com> - 20111120git4a25390-3
- Fix license
- More specific URL

* Tue Nov 22 2011 Ivan Afonichev <ivan.afonichev@gmail.com> - 20111120git4a25390-2
- Require udev

* Sun Nov 20 2011 Ivan Afonichev <ivan.afonichev@gmail.com> - 20111120git4a25390-1
- Versioning changes
- Use only needed sources
- Udev rules moved to lib
- More license info added
- adb and fastboot moved to provides from summary

* Tue Nov 15 2011 Ivan Afonichev <ivan.afonichev@gmail.com> - 20111115.4a25390-1
- Change upstream git repo URL
- Update to upstream git commit 4a25390
- Added more udev devices

* Mon Oct 17 2011 Ivan Afonichev <ivan.afonichev@gmail.com> - 20110816.80d508f-3
- Update udev rules (s/SYSFS/ATTR/g) 

* Sat Aug 27 2011 Ivan Afonichev <ivan.afonichev@gmail.com> - 20110816.80d508f-2
- Remove the rm in the install section
- Remove defattr
- Use install command(not macro)
- Add description of fastboot

* Tue Aug 16 2011 Ivan Afonichev <ivan.afonichev@gmail.com> - 20110816.80d508f-1
- Update to upstream git commit 80d508f
- Added more udev devices

* Sun Jul 31 2011 Ivan Afonichev <ivan.afonichev@gmail.com> - 20110731.810cf41-1
- Update to upstream git commit 810cf41
- Fix License
- Use optflags
- Added more udev devices
- Remove Epoch

* Tue Jul 26 2011 Ivan Afonichev <ivan.afonichev@gmail.com> - 0:20110726.212282c-1
- Update to upstream git commit 212282c

* Wed May 18 2011 Ivan Afonichev <ivan.afonichev@gmail.com> - 0:20110516.327b2b7-1
- Initial spec
- Initial makefiles
- Initial udev rule
