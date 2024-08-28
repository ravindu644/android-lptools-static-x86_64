%global _hardened_build 1

Name:          android-tools
Version:       35.0.1
Release:       %autorelease
Epoch:         1
Summary:       Android platform tools(adb, fastboot)

# The entire source code is ASL 2.0 except boringssl which is BSD
# Automatically converted from old format: ASL 2.0 and (ASL 2.0 and BSD) - review is highly recommended.
License:       Apache-2.0 AND (Apache-2.0 AND LicenseRef-Callaway-BSD)
URL:           http://developer.android.com/guide/developing/tools/

#  Sources with all needed patches and cmakelists live there now: 
Source0:       https://github.com/nmeum/%{name}/releases/download/%{version}/%{name}-%{version}.tar.xz
Source1:       51-android.rules
Source2:       adb.service

BuildRequires: brotli-devel
BuildRequires: cmake
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: gtest-devel
BuildRequires: golang
BuildRequires: golang(golang.org/x/crypto/chacha20)
BuildRequires: golang(golang.org/x/crypto/chacha20poly1305)
BuildRequires: golang(golang.org/x/crypto/curve25519)
BuildRequires: golang(golang.org/x/crypto/hkdf)
BuildRequires: golang(golang.org/x/crypto/xts)
BuildRequires: libusbx-devel
BuildRequires: libzstd-devel
BuildRequires: lz4-devel
BuildRequires: multilib-rpm-config
BuildRequires: pcre2-devel
BuildRequires: perl
BuildRequires: protobuf-devel
BuildRequires: systemd-rpm-macros

Provides:      adb = %{epoch}:%{version}-%{release}
Provides:      fastboot = %{epoch}:%{version}-%{release}
Provides:      mke2fs.android = %{epoch}:%{version}-%{release}

# Bundled bits
Provides: bundled(boringssl)

# Bundled boringssl doesn't support the big endian architectures rhbz 1431379
# And dropped ppc64le support: https://github.com/google/boringssl/commit/7d2338d000eb1468a5bbf78e91854236e18fb9e4
ExcludeArch: ppc ppc64 s390x ppc64le

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
%autosetup -p1
cp -p %{SOURCE1} 51-android.rules

%build
export GO111MODULE=off
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
%doc 51-android.rules
%{_unitdir}/adb.service
%attr(0755,root,root) %dir %{_sharedstatedir}/adb
%attr(0755,root,root) %dir %{_datadir}/android-tools
#ASL2.0 and BSD
%{_bindir}/adb
#ASL2.0
%{_bindir}/avbtool
%{_bindir}/mke2fs.android
%{_bindir}/simg2img
%{_bindir}/img2simg
%{_bindir}/fastboot
%{_bindir}/append2simg
%{_bindir}/e2fsdroid
%{_bindir}/ext2simg
%{_bindir}/lpadd
%{_bindir}/lpdump
%{_bindir}/lpflash
%{_bindir}/lpmake
%{_bindir}/lpunpack
%{_bindir}/make_f2fs
%{_bindir}/mkbootimg
%{_bindir}/mkdtboimg
%{_bindir}/repack_bootimg
%{_bindir}/sload_f2fs
%{_bindir}/unpack_bootimg
%{_datadir}/android-tools/completions/adb
%{_datadir}/android-tools/completions/fastboot
%{_datadir}/android-tools/mkbootimg/gki/generate_gki_certificate.py
%{_datadir}/android-tools/mkbootimg/mkbootimg.py
%{_datadir}/bash-completion/completions/adb
%{_datadir}/bash-completion/completions/fastboot

%changelog
%autochangelog
