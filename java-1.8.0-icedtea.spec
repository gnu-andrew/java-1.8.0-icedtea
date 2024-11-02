# Copyright (C) 2024 Red Hat, Inc.
# Written by Andrew John Hughes <gnu.andrew@redhat.com>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

%define icedteabranch 3.33
%define icedteaver %{icedteabranch}.0
%define icedteasnapshot %{nil}

%define icedteaurl http://icedtea.classpath.org
%define openjdkurl http://hg.openjdk.java.net
%define dropurl %{icedteaurl}/download/drops
%define repourl %{dropurl}/icedtea8/%{icedteaver}

%define openjdkchangeset 1df1fdee64
%define shenandoahchangeset 07b0a0acfd
%define aarch32changeset e7e90c82b3

%global aarch64 aarch64 arm64 armv8
%global ppc64le	ppc64le
%global ppc64be	ppc64 ppc64p7

%define multilib_arches %{ppc64be} sparc64 x86_64
%define jit_arches %{arm} %{aarch64} %{ix86} x86_64 sparcv9 sparc64 %{power64}
%define jfr_arches %{jit_arches}
# Set of architectures for which we build the Shenandoah garbage collector
%global shenandoah_arches noarch

# In some cases, the arch used by the JDK does
# not match _arch.
# Also, in some cases, the machine name used by SystemTap
# does not match that given by _build_cpu
%ifarch x86_64
%global stapinstall x86_64
%endif
%ifarch %{ppc64be}
%global stapinstall powerpc
%endif
%ifarch %{ppc64le}
%global stapinstall powerpc
%endif
%ifarch i386
%global stapinstall i386
%endif
%ifarch i686
%global stapinstall i386
%endif
# 32 bit sparc, optimized for v9
%ifarch sparcv9
%global stapinstall %{_build_cpu}
%endif
# 64 bit sparc
%ifarch sparc64
%global stapinstall %{_build_cpu}
%endif
%ifarch %{arm}
%global stapinstall arm
%endif
%ifarch %{aarch64}
%global stapinstall arm64
%endif
%ifarch ia64
%global stapinstall ia64
%endif
%ifarch s390
%global stapinstall s390
%endif
%ifarch s390x
%global stapinstall s390
%endif
%ifarch ppc
%global stapinstall powerpc
%endif
# Need to support noarch for srpm build
%ifarch noarch
%global stapinstall %{nil}
%endif

# If bootstrap is 1, OpenJDK is bootstrapped against
# java-1.7.0-openjdk-devel, then rebuilt with itself.
# If bootstrap is 0, OpenJDK is built against
# java-1.7.0-openjdk-devel.
%ifnarch %{jit_arches}
%define bootstrap 0
%else
%define bootstrap 1
%endif

%if 0%{?fedora} > 21
%ifarch %{arm}
%define bootstrap_jdk java-1.8.0-openjdk-aarch32-devel
%define bootstrap_path /usr/lib/jvm/java-1.8.0-openjdk-aarch32
%else
%define bootstrap_jdk java-1.8.0-openjdk-devel
%define bootstrap_path /usr/lib/jvm/java-1.8.0-openjdk
%endif
%else
%if 0%{?rhel} <= 7
%define bootstrap_jdk java-1.7.0-openjdk-devel
%if 0%{?rhel} < 7
%define bootstrap_path /usr/lib/jvm/%{bootstrap_name}
%else
%define bootstrap_path /usr/lib/jvm/java-1.7.0-openjdk
%endif
%else
%define bootstrap_jdk java-1.8.0-openjdk-devel
%define bootstrap_path /usr/lib/jvm/java-1.8.0-openjdk
%endif
%endif

# If debug is 1, a debug build of OpenJDK is performed.
%define debug 0

# Define havelcms2 to 1 if the platform has lcms2 >= 2.11
# Only Fedora >= 33 does at present
%if 0%{?fedora}
%if 0%{?fedora} < 33
%define havelcms2 0
%else
%define havelcms2 1
%endif
%else
%define havelcms2 0
%endif

%if %{debug}
%define debugbuild icedtea-debug
%else
%define debugbuild %{nil}
%endif

%define buildoutputdir openjdk.build

%if %{bootstrap}
%define bootstrapopt %{nil}
%else
%define bootstrapopt --disable-bootstrap
%endif

# Enable the PKCS11 provider.
%define pkcs11opt --enable-nss

# Turn on use of the system LCMS 2 library if
# available. If not, use the in-tree version.
%if %{havelcms2}
%define lcmsopt --enable-system-lcms
%else
%define lcmsopt --disable-system-lcms
%endif

# Use Shenandoah on x86_64 and aarch64
# Also enabled on ppc64be and s390 to check it at least builds on these architectures
%ifarch %{shenandoah_arches}
%define hsopt --with-hotspot-build=shenandoah --with-hotspot-src-zip=%{SOURCE3}
%else
%ifarch %{arm}
%define hsopt --with-hotspot-src-zip=%{SOURCE4}
%else
%define hsopt %{nil}
%endif
%endif

# Convert an absolute path to a relative path.  Each symbolic link is
# specified relative to the directory in which it is installed so that
# it will resolve properly within chrooted installations.
%define script 'use File::Spec; print File::Spec->abs2rel($ARGV[0], $ARGV[1])'
%define abs2rel %{__perl} -e %{script}

# Hard-code libdir on 64-bit architectures to make the 64-bit JDK
# simply be another alternative.
%ifarch %{multilib_arches}
%define syslibdir	%{_prefix}/lib64
%define _libdir         %{_prefix}/lib
%define archname        %{name}.%{_arch}
%define bootstrap_name  java-1.7.0-openjdk.%{_arch}
%else
%define syslibdir       %{_libdir}
%define archname        %{name}
%define bootstrap_name  java-1.7.0-openjdk
%endif

# Standard JPackage naming and versioning defines.
%define origin          icedtea
%define priority        16000
%define javaver         1.8.0

# Standard JPackage directories and symbolic links.
# Make 64-bit JDKs just another alternative on 64-bit architectures.
%ifarch %{multilib_arches}
%define sdklnk          java-%{javaver}-%{origin}.%{_arch}
%define jrelnk          jre-%{javaver}-%{origin}.%{_arch}
%define sdkdir          %{name}-%{version}.%{_arch}
%else
%define sdklnk          java-%{javaver}-%{origin}
%define jrelnk          jre-%{javaver}-%{origin}
%define sdkdir          %{name}-%{version}
%endif
%define jredir          %{sdkdir}/jre
%define sdkbindir       %{_jvmdir}/%{sdklnk}/bin
%define jrebindir       %{_jvmdir}/%{jrelnk}/bin
%ifarch %{multilib_arches}
%define jvmjardir       %{?_jvmjardir:%{_jvmjardir}/%{name}-%{version}.%{_arch}}
%else
%define jvmjardir       %{?_jvmjardir:%{_jvmjardir}/%{name}-%{version}}
%endif

# Where to install systemtap tapset (links)
# We would like these to be in a package specific subdir,
# but currently systemtap doesn't support that, so we have to
# use the root tapset dir for now. To distinquish between 64
# and 32 bit architectures we place the tapsets under the arch
# specific dir (note that systemtap will only pickup the tapset
# for the primary arch for now). Systemtap uses the machine name
# aka build_cpu as architecture specific directory name.
%global tapsetroot /usr/share/systemtap
%global tapsetdir %{tapsetroot}/tapset/%{stapinstall}

# Prevent brp-java-repack-jars from being run.
%define __jar_repack 0

Name:    java-%{javaver}-%{origin}
Version: %{icedteaver}
Release: 1%{?dist}
# java-1.5.0-ibm from jpackage.org set Epoch to 1 for unknown reasons,
# and this change was brought into RHEL-4.  java-1.5.0-ibm packages
# also included the epoch in their virtual provides.  This created a
# situation where in-the-wild java-1.5.0-ibm packages provided "java =
# 1:1.5.0".  In RPM terms, "1.6.0 < 1:1.5.0" since 1.6.0 is
# interpreted as 0:1.6.0.  So the "java >= 1.6.0" requirement would be
# satisfied by the 1:1.5.0 packages.  Thus we need to set the epoch in
# JDK package >= 1.6.0 to 1, and packages referring to JDK virtual
# provides >= 1.6.0 must specify the epoch, "java >= 1:1.6.0".
Epoch:   1
Summary: OpenJDK Runtime Environment
Group:   Development/Languages

License:  ASL 1.1, ASL 2.0, GPL+, GPLv2, GPLv2 with exceptions, LGPL+, LGPLv2, MPLv1.0, MPLv1.1, Public Domain, W3C
URL:      http://icedtea.classpath.org/
Source0:  %{icedteaurl}/download/source/icedtea-%{icedteaver}%{icedteasnapshot}.tar.xz
Source1:  README.src
Source2:  %{repourl}/openjdk-git.tar.xz#/openjdk-%{openjdkchangeset}.tar.xz
Source3:  %{repourl}/shenandoah-git.tar.xz#/shenandoah-%{shenandoahchangeset}.tar.xz
Source4:  %{repourl}/aarch32-git.tar.xz#/aarch32-%{aarch32changeset}.tar.xz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: alsa-lib-devel
BuildRequires: cups-devel
BuildRequires: desktop-file-utils
BuildRequires: libX11-devel
BuildRequires: libXi-devel
BuildRequires: libXt-devel
BuildRequires: libXtst-devel
BuildRequires: libXext-devel
BuildRequires: libXrender-devel
BuildRequires: libXau-devel
BuildRequires: libXinerama-devel
BuildRequires: libXcomposite-devel
BuildRequires: zlib-devel
BuildRequires: libjpeg-devel
BuildRequires: libpng-devel
BuildRequires: giflib-devel
%if %{havelcms2}
BuildRequires: lcms2-devel >= 2.11
%endif
BuildRequires: xorg-x11-proto-devel
BuildRequires: freetype-devel
# Provides lsb_release for generating distro id in jdk_generic_profile.sh
BuildRequires: redhat-lsb-core
BuildRequires: nss-devel
BuildRequires: libattr-devel
BuildRequires: %{bootstrap_jdk}
BuildRequires: pkgconfig >= 0.9.0
%if 0%{?fedora} < 36
BuildRequires: xorg-x11-utils
%endif
# Zero-assembler build requirement.
%ifnarch %{jit_arches}
BuildRequires: libffi-devel
%endif
# For obtaining Kerberos cache location
BuildRequires: krb5-devel
# Required for smartcard support
BuildRequires: pcsc-lite-devel
# Required for SCTP support
BuildRequires: lksctp-tools-devel
# For improved font rendering
BuildRequires: fontconfig-devel

# OpenJDK build requirement for creating src.zip
BuildRequires: zip
# cacerts build requirement.
BuildRequires: openssl
#systemtap build requirement.
BuildRequires: systemtap-sdt-devel
# For javac script and SystemTap tests
BuildRequires: perl

Requires: libjpeg = 6b
# Require /etc/pki/java/cacerts.
Requires: ca-certificates
# Require jpackage-utils for ant.
Requires: jpackage-utils >= 1.7.3-1jpp.2
# Require zoneinfo data provided by tzdata-java subpackage.
Requires: tzdata-java
# Gtk+ look and feel
Requires: gtk2
# Post requires alternatives to install tool alternatives.
Requires(post):   %{_sbindir}/alternatives
# Postun requires alternatives to uninstall tool alternatives.
Requires(postun): %{_sbindir}/alternatives

# Standard JPackage base provides.
Provides: jre-%{javaver}-%{origin} = %{epoch}:%{version}-%{release}
Provides: jre-%{origin} = %{epoch}:%{version}-%{release}
Provides: jre-%{javaver} = %{epoch}:%{version}-%{release}
Provides: java-%{javaver} = %{epoch}:%{version}-%{release}
Provides: jre = %{javaver}
Provides: java-%{origin} = %{epoch}:%{version}-%{release}
Provides: java = %{epoch}:%{javaver}
# Standard JPackage extensions provides.
Provides: jndi = %{epoch}:%{version}
Provides: jndi-ldap = %{epoch}:%{version}
Provides: jndi-cos = %{epoch}:%{version}
Provides: jndi-rmi = %{epoch}:%{version}
Provides: jndi-dns = %{epoch}:%{version}
Provides: jaas = %{epoch}:%{version}
Provides: jsse = %{epoch}:%{version}
Provides: jce = %{epoch}:%{version}
Provides: jdbc-stdext = 3.0
Provides: java-sasl = %{epoch}:%{version}
Provides: java-fonts = %{epoch}:%{version}

%description
The OpenJDK runtime environment.

%package devel
Summary: OpenJDK Development Environment
Group:   Development/Tools

# Require base package.
Requires:         %{name} = %{epoch}:%{version}-%{release}
# Post requires alternatives to install tool alternatives.
Requires(post):   %{_sbindir}/alternatives
# Postun requires alternatives to uninstall tool alternatives.
Requires(postun): %{_sbindir}/alternatives

# Standard JPackage devel provides.
Provides: java-sdk-%{javaver}-%{origin} = %{epoch}:%{version}
Provides: java-sdk-%{javaver} = %{epoch}:%{version}
Provides: java-sdk-%{origin} = %{epoch}:%{version}
Provides: java-sdk = %{epoch}:%{javaver}
Provides: java-%{javaver}-devel = %{epoch}:%{version}
Provides: java-devel-%{origin} = %{epoch}:%{version}
Provides: java-devel = %{epoch}:%{javaver}


%description devel
The OpenJDK development tools.

%package demo
Summary: OpenJDK Demos
Group:   Development/Languages

Requires: %{name} = %{epoch}:%{version}-%{release}

%description demo
The OpenJDK demos.

%package src
Summary: OpenJDK Source Bundle
Group:   Development/Languages

Requires: %{name} = %{epoch}:%{version}-%{release}

%description src
The OpenJDK source bundle.

%package javadoc
Summary: OpenJDK API Documentation
Group:   Documentation

# Post requires alternatives to install javadoc alternative.
Requires(post):   %{_sbindir}/alternatives
# Postun requires alternatives to uninstall javadoc alternative.
Requires(postun): %{_sbindir}/alternatives

# Standard JPackage javadoc provides.
Provides: java-javadoc = %{epoch}:%{version}-%{release}
Provides: java-%{javaver}-javadoc = %{epoch}:%{version}-%{release}

%description javadoc
The OpenJDK API documentation.

%prep

# Using the echo macro breaks rpmdev-bumpspec, as it parses the first line of stdout :-(
%if 0%{?stapinstall:1}
  echo "CPU: %{_target_cpu}, SystemTap install directory: %{stapinstall}"
%else
  %{error:Unrecognised architecture %{_target_cpu}}
%endif

%setup -q -n icedtea-%{icedteaver}%{icedteasnapshot}

cp %{SOURCE1} .

%build

# This package fails to build with LTO due to undefined symbols
# (_ZN14G1CMOopClosure9do_oop_nvIjEEvPT or
# void G1CMOopClosure::do_oop_nv<unsigned int>(unsigned int*))
# LTO was disabled in OpenSuSE as well, but with no real explanation why
# beyond the undefined symbols.  It really should be investigated further.
# Disable LTO
%define _lto_cflags %{nil}

# Filter out flags from CFLAGS & CXXFLAGS that cause problems with the OpenJDK build
# We filter out -O flags so that the optimisation of HotSpot is not lowered from O3 to O2
# We filter out -Wall which will otherwise cause HotSpot to produce hundreds of thousands of warnings (100+mb logs)
# We replace it with -Wformat (required by -Werror=format-security) and -Wno-cpp to avoid FORTIFY_SOURCE warnings
# We filter out -fexceptions as the HotSpot build explicitly does -fno-exceptions and it's otherwise the default for C++
CFLAGS=$(echo %{optflags}|sed -e 's|-Wall|-Wformat -Wno-cpp|'|sed -r -e 's|-O[0-9]*||'|sed -e 's|-fexceptions||')
CXXFLAGS=$(echo %{optflags}|sed -e 's|-Wall|-Wformat -Wno-cpp|'|sed -r -e 's|-O[0-9]*||'|sed -e 's|-fexceptions||')

# Build IcedTea and OpenJDK.
%configure %{bootstrapopt} --prefix=%{_jvmdir}/%{sdkdir} --exec-prefix=%{_jvmdir}/%{sdkdir} \
  --bindir=%{_jvmdir}/%{sdkdir}/bin --includedir=%{_jvmdir}/%{sdkdir}/include \
  --docdir=%{_defaultdocdir}/%{name} --mandir=%{_jvmdir}/%{sdkdir}/man \
  --htmldir=%{_javadocdir}/%{name} --with-openjdk-src-zip=%{SOURCE2} %{hsopt} \
%ifarch %{jfr_arches}
    --enable-jfr \
%else
    --disable-jfr \
%endif
  --disable-downloading %{pkcs11opt} %{lcmsopt} --disable-tests --disable-systemtap-tests \
  --enable-improved-font-rendering --enable-Werror --disable-precompiled-headers

make %{?_smp_mflags} %{debugbuild}

%check

make check

%install
rm -rf $RPM_BUILD_ROOT
STRIP_KEEP_SYMTAB=libjvm*

%make_install

# Install extension symlinks.
%{?_jvmjardir:
install -d -m 755 $RPM_BUILD_ROOT%{jvmjardir}
pushd $RPM_BUILD_ROOT%{jvmjardir}
  RELATIVE=$(%{abs2rel} %{_jvmdir}/%{jredir}/lib %{jvmjardir})
  ln -sf $RELATIVE/jsse.jar jsse-%{version}.jar
  ln -sf $RELATIVE/jce.jar jce-%{version}.jar
  ln -sf $RELATIVE/rt.jar jndi-%{version}.jar
  ln -sf $RELATIVE/rt.jar jndi-ldap-%{version}.jar
  ln -sf $RELATIVE/rt.jar jndi-cos-%{version}.jar
  ln -sf $RELATIVE/rt.jar jndi-rmi-%{version}.jar
  ln -sf $RELATIVE/rt.jar jaas-%{version}.jar
  ln -sf $RELATIVE/rt.jar jdbc-stdext-%{version}.jar
  ln -sf jdbc-stdext-%{version}.jar jdbc-stdext-3.0.jar
  ln -sf $RELATIVE/rt.jar sasl-%{version}.jar
  for jar in *-%{version}.jar
  do
    if [ x%{version} != x%{javaver} ]
    then
      ln -sf $jar $(echo $jar | sed "s|-%{version}.jar|-%{javaver}.jar|g")
    fi
    ln -sf $jar $(echo $jar | sed "s|-%{version}.jar|.jar|g")
  done
popd}

# Install JCE policy symlinks.
install -d -m 755 $RPM_BUILD_ROOT%{_jvmprivdir}/%{archname}/jce/vanilla

# Install versionless symlinks.
pushd %{buildroot}%{_jvmdir}
  ln -sf %{jredir} %{jrelnk}
  ln -sf %{sdkdir} %{sdklnk}
popd

%{?_jvmjardir:
pushd %{buildroot}%{_jvmjardir}
  ln -sf %{sdkdir} %{jrelnk}
  ln -sf %{sdkdir} %{sdklnk}
popd}

# Install man pages.
install -d -m 755 $RPM_BUILD_ROOT%{_mandir}/man1
for manpage in %{buildroot}%{_jvmdir}/%{sdkdir}/man/man1/*
do
  # Convert man pages to UTF8 encoding.
  iconv -f ISO_8859-1 -t UTF8 $manpage -o $manpage.tmp
  mv -f $manpage.tmp $manpage
  install -m 644 -p $manpage $RPM_BUILD_ROOT%{_mandir}/man1/$(basename $manpage .1)-%{name}.1
done
# Delete the man pages installed by IcedTea so RPM doesn't complain
rm -rf %{buildroot}%{_jvmdir}/%{sdkdir}/man

# Install desktop files.
for e in jconsole policytool ; do
    mv $RPM_BUILD_ROOT%{_datadir}/applications/$e{-%{javaver},}.desktop
    desktop-file-install --vendor=%{name} --mode=644 --delete-original \
        --dir=$RPM_BUILD_ROOT%{_datadir}/applications \
	$RPM_BUILD_ROOT%{_datadir}/applications/$e.desktop
done

# Find JRE directories.
find $RPM_BUILD_ROOT%{_jvmdir}/%{jredir} -type d \
  | grep -v jre/lib/security \
  | sed 's|'$RPM_BUILD_ROOT'|%dir |' \
  > %{name}.files
# Find JRE files.
find $RPM_BUILD_ROOT%{_jvmdir}/%{jredir} -type f -o -type l \
  | grep -v jre/lib/security \
  | sed 's|'$RPM_BUILD_ROOT'||' \
  >> %{name}.files
# Find demo directories.
find $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/demo \
  $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/sample -type d \
  | sed 's|'$RPM_BUILD_ROOT'|%dir |' \
  > %{name}-demo.files

# FIXME: remove SONAME entries from demo DSOs.  See
# https://bugzilla.redhat.com/show_bug.cgi?id=436497

# Find non-documentation demo files.
find $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/demo \
  $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/sample \
  -type f -o -type l | sort \
  | grep -v README \
  | sed 's|'$RPM_BUILD_ROOT'||' \
  >> %{name}-demo.files
# Find documentation demo files.
find $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/demo \
  $RPM_BUILD_ROOT%{_jvmdir}/%{sdkdir}/sample \
  -type f -o -type l | sort \
  | grep README \
  | sed 's|'$RPM_BUILD_ROOT'||' \
  | sed 's|^|%doc |' \
  >> %{name}-demo.files

%clean
rm -rf $RPM_BUILD_ROOT

# FIXME: identical binaries are copied, not linked. This needs to be
# fixed upstream.
%post
ext=.gz
alternatives \
  --install %{_bindir}/java java %{jrebindir}/java %{priority} \
  --slave %{_jvmdir}/jre jre %{_jvmdir}/%{jrelnk} \
  %{?_jvmjardir:--slave %{_jvmjardir}/jre jre_exports %{_jvmjardir}/%{jrelnk}} \
  --slave %{_bindir}/keytool keytool %{jrebindir}/keytool \
  --slave %{_bindir}/orbd orbd %{jrebindir}/orbd \
  --slave %{_bindir}/pack200 pack200 %{jrebindir}/pack200 \
  --slave %{_bindir}/rmid rmid %{jrebindir}/rmid \
  --slave %{_bindir}/rmiregistry rmiregistry %{jrebindir}/rmiregistry \
  --slave %{_bindir}/servertool servertool %{jrebindir}/servertool \
  --slave %{_bindir}/tnameserv tnameserv %{jrebindir}/tnameserv \
  --slave %{_bindir}/unpack200 unpack200 %{jrebindir}/unpack200 \
  --slave %{_mandir}/man1/java.1$ext java.1$ext \
  %{_mandir}/man1/java-%{name}.1$ext \
  --slave %{_mandir}/man1/keytool.1$ext keytool.1$ext \
  %{_mandir}/man1/keytool-%{name}.1$ext \
  --slave %{_mandir}/man1/orbd.1$ext orbd.1$ext \
  %{_mandir}/man1/orbd-%{name}.1$ext \
  --slave %{_mandir}/man1/pack200.1$ext pack200.1$ext \
  %{_mandir}/man1/pack200-%{name}.1$ext \
  --slave %{_mandir}/man1/rmid.1$ext rmid.1$ext \
  %{_mandir}/man1/rmid-%{name}.1$ext \
  --slave %{_mandir}/man1/rmiregistry.1$ext rmiregistry.1$ext \
  %{_mandir}/man1/rmiregistry-%{name}.1$ext \
  --slave %{_mandir}/man1/servertool.1$ext servertool.1$ext \
  %{_mandir}/man1/servertool-%{name}.1$ext \
  --slave %{_mandir}/man1/tnameserv.1$ext tnameserv.1$ext \
  %{_mandir}/man1/tnameserv-%{name}.1$ext \
  --slave %{_mandir}/man1/unpack200.1$ext unpack200.1$ext \
  %{_mandir}/man1/unpack200-%{name}.1$ext

alternatives \
  --install %{_jvmdir}/jre-%{origin} \
  jre_%{origin} %{_jvmdir}/%{jrelnk} %{priority} \
  %{?_jvmjardir:--slave %{_jvmjardir}/jre-%{origin} \
    jre_%{origin}_exports %{_jvmjardir}/%{jrelnk}}

alternatives \
  --install %{_jvmdir}/jre-%{javaver} \
  jre_%{javaver} %{_jvmdir}/%{jrelnk} %{priority} \
  %{?_jvmjardir:--slave %{_jvmjardir}/jre-%{javaver} \
    jre_%{javaver}_exports %{_jvmjardir}/%{jrelnk}}

# Update for jnlp handling.
update-desktop-database %{_datadir}/applications &> /dev/null || :

touch --no-create %{_datadir}/icons/hicolor
if [ -x %{_bindir}/gtk-update-icon-cache ] ; then
  %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor
fi

exit 0

%postun
if [ $1 -eq 0 ]
then
  alternatives --remove java %{jrebindir}/java
  alternatives --remove jre_%{origin} %{_jvmdir}/%{jrelnk}
  alternatives --remove jre_%{javaver} %{_jvmdir}/%{jrelnk}
fi

# Update for jnlp handling.
update-desktop-database %{_datadir}/applications &> /dev/null || :

touch --no-create %{_datadir}/icons/hicolor
if [ -x %{_bindir}/gtk-update-icon-cache ] ; then
  %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor
fi

exit 0

%post devel
ext=.gz
alternatives \
  --install %{_bindir}/javac javac %{sdkbindir}/javac %{priority} \
  --slave %{_jvmdir}/java java_sdk %{_jvmdir}/%{sdklnk} \
  {?_jvmjardir:--slave %{_jvmjardir}/java java_sdk_exports %{_jvmjardir}/%{sdklnk}} \
  --slave %{_bindir}/appletviewer appletviewer %{sdkbindir}/appletviewer \
  --slave %{_bindir}/apt apt %{sdkbindir}/apt \
  --slave %{_bindir}/extcheck extcheck %{sdkbindir}/extcheck \
  --slave %{_bindir}/jar jar %{sdkbindir}/jar \
  --slave %{_bindir}/jarsigner jarsigner %{sdkbindir}/jarsigner \
  --slave %{_bindir}/javadoc javadoc %{sdkbindir}/javadoc \
  --slave %{_bindir}/javah javah %{sdkbindir}/javah \
  --slave %{_bindir}/javap javap %{sdkbindir}/javap \
  --slave %{_bindir}/jcmd jcmd %{sdkbindir}/jcmd \
  --slave %{_bindir}/jconsole jconsole %{sdkbindir}/jconsole \
  --slave %{_bindir}/jdb jdb %{sdkbindir}/jdb \
  --slave %{_bindir}/jhat jhat %{sdkbindir}/jhat \
  --slave %{_bindir}/jinfo jinfo %{sdkbindir}/jinfo \
  --slave %{_bindir}/jmap jmap %{sdkbindir}/jmap \
  --slave %{_bindir}/jps jps %{sdkbindir}/jps \
  --slave %{_bindir}/jrunscript jrunscript %{sdkbindir}/jrunscript \
  --slave %{_bindir}/jsadebugd jsadebugd %{sdkbindir}/jsadebugd \
  --slave %{_bindir}/jstack jstack %{sdkbindir}/jstack \
  --slave %{_bindir}/jstat jstat %{sdkbindir}/jstat \
  --slave %{_bindir}/jstatd jstatd %{sdkbindir}/jstatd \
  --slave %{_bindir}/native2ascii native2ascii %{sdkbindir}/native2ascii \
  --slave %{_bindir}/policytool policytool %{sdkbindir}/policytool \
  --slave %{_bindir}/rmic rmic %{sdkbindir}/rmic \
  --slave %{_bindir}/schemagen schemagen %{sdkbindir}/schemagen \
  --slave %{_bindir}/serialver serialver %{sdkbindir}/serialver \
  --slave %{_bindir}/wsgen wsgen %{sdkbindir}/wsgen \
  --slave %{_bindir}/wsimport wsimport %{sdkbindir}/wsimport \
  --slave %{_bindir}/xjc xjc %{sdkbindir}/xjc \
  --slave %{_mandir}/man1/appletviewer.1$ext appletviewer.1$ext \
  %{_mandir}/man1/appletviewer-%{name}.1$ext \
  --slave %{_mandir}/man1/apt.1$ext apt.1$ext \
  %{_mandir}/man1/apt-%{name}.1$ext \
  --slave %{_mandir}/man1/extcheck.1$ext extcheck.1$ext \
  %{_mandir}/man1/extcheck-%{name}.1$ext \
  --slave %{_mandir}/man1/jar.1$ext jar.1$ext \
  %{_mandir}/man1/jar-%{name}.1$ext \
  --slave %{_mandir}/man1/jarsigner.1$ext jarsigner.1$ext \
  %{_mandir}/man1/jarsigner-%{name}.1$ext \
  --slave %{_mandir}/man1/javac.1$ext javac.1$ext \
  %{_mandir}/man1/javac-%{name}.1$ext \
  --slave %{_mandir}/man1/javadoc.1$ext javadoc.1$ext \
  %{_mandir}/man1/javadoc-%{name}.1$ext \
  --slave %{_mandir}/man1/javah.1$ext javah.1$ext \
  %{_mandir}/man1/javah-%{name}.1$ext \
  --slave %{_mandir}/man1/javap.1$ext javap.1$ext \
  %{_mandir}/man1/javap-%{name}.1$ext \
  --slave %{_mandir}/man1/jcmd.1$ext jcmd.1$ext \
  %{_mandir}/man1/jcmd-%{name}.1$ext \
  --slave %{_mandir}/man1/jconsole.1$ext jconsole.1$ext \
  %{_mandir}/man1/jconsole-%{name}.1$ext \
  --slave %{_mandir}/man1/jdb.1$ext jdb.1$ext \
  %{_mandir}/man1/jdb-%{name}.1$ext \
  --slave %{_mandir}/man1/jhat.1$ext jhat.1$ext \
  %{_mandir}/man1/jhat-%{name}.1$ext \
  --slave %{_mandir}/man1/jinfo.1$ext jinfo.1$ext \
  %{_mandir}/man1/jinfo-%{name}.1$ext \
  --slave %{_mandir}/man1/jmap.1$ext jmap.1$ext \
  %{_mandir}/man1/jmap-%{name}.1$ext \
  --slave %{_mandir}/man1/jps.1$ext jps.1$ext \
  %{_mandir}/man1/jps-%{name}.1$ext \
  --slave %{_mandir}/man1/jrunscript.1$ext jrunscript.1$ext \
  %{_mandir}/man1/jrunscript-%{name}.1$ext \
  --slave %{_mandir}/man1/jsadebugd.1$ext jsadebugd.1$ext \
  %{_mandir}/man1/jsadebugd-%{name}.1$ext \
  --slave %{_mandir}/man1/jstack.1$ext jstack.1$ext \
  %{_mandir}/man1/jstack-%{name}.1$ext \
  --slave %{_mandir}/man1/jstat.1$ext jstat.1$ext \
  %{_mandir}/man1/jstat-%{name}.1$ext \
  --slave %{_mandir}/man1/jstatd.1$ext jstatd.1$ext \
  %{_mandir}/man1/jstatd-%{name}.1$ext \
  --slave %{_mandir}/man1/native2ascii.1$ext native2ascii.1$ext \
  %{_mandir}/man1/native2ascii-%{name}.1$ext \
  --slave %{_mandir}/man1/policytool.1$ext policytool.1$ext \
  %{_mandir}/man1/policytool-%{name}.1$ext \
  --slave %{_mandir}/man1/rmic.1$ext rmic.1$ext \
  %{_mandir}/man1/rmic-%{name}.1$ext \
  --slave %{_mandir}/man1/schemagen.1$ext schemagen.1$ext \
  %{_mandir}/man1/schemagen-%{name}.1$ext \
  --slave %{_mandir}/man1/serialver.1$ext serialver.1$ext \
  %{_mandir}/man1/serialver-%{name}.1$ext \
  --slave %{_mandir}/man1/wsgen.1$ext wsgen.1$ext \
  %{_mandir}/man1/wsgen-%{name}.1$ext \
  --slave %{_mandir}/man1/wsimport.1$ext wsimport.1$ext \
  %{_mandir}/man1/wsimport-%{name}.1$ext \
  --slave %{_mandir}/man1/xjc.1$ext xjc.1$ext \
  %{_mandir}/man1/xjc-%{name}.1$ext

alternatives \
  --install %{_jvmdir}/java-%{origin} \
  java_sdk_%{origin} %{_jvmdir}/%{sdklnk} %{priority} \
  %{?_jvmjardir:--slave %{_jvmjardir}/java-%{origin} \
    java_sdk_%{origin}_exports %{_jvmjardir}/%{sdklnk}}

alternatives \
  --install %{_jvmdir}/java-%{javaver} \
  java_sdk_%{javaver} %{_jvmdir}/%{sdklnk} %{priority} \
  %{?_jvmjardir:--slave %{_jvmjardir}/java-%{javaver} \
    java_sdk_%{javaver}_exports %{_jvmjardir}/%{sdklnk}}

exit 0

%postun devel
if [ $1 -eq 0 ]
then
  alternatives --remove javac %{sdkbindir}/javac
  alternatives --remove java_sdk_%{origin} %{_jvmdir}/%{sdklnk}
  alternatives --remove java_sdk_%{javaver} %{_jvmdir}/%{sdklnk}
fi

exit 0

%post javadoc
alternatives \
  --install %{_javadocdir}/java javadocdir %{_javadocdir}/%{name}/api \
  %{priority}

exit 0

%postun javadoc
if [ $1 -eq 0 ]
then
  alternatives --remove javadocdir %{_javadocdir}/%{name}/api
fi

exit 0


%files -f %{name}.files
%defattr(-,root,root,-)
%docdir %{_defaultdocdir}/%{name}
%{_defaultdocdir}/%{name}
%dir %{_jvmdir}/%{sdkdir}
%{_jvmdir}/%{sdkdir}/release
%{_jvmdir}/%{jrelnk}
%{?_jvmjardir:%{_jvmjardir}/%{jrelnk}}
%{_jvmprivdir}/*
%{?_jvmjardir:%{jvmjardir}}
%dir %{_jvmdir}/%{jredir}/lib/security
%{_jvmdir}/%{jredir}/lib/security/cacerts
%config(noreplace) %{_jvmdir}/%{jredir}/lib/security/java.policy
%config(noreplace) %{_jvmdir}/%{jredir}/lib/security/java.security
%config(noreplace) %{_jvmdir}/%{jredir}/lib/security/nss.cfg
%config(noreplace) %{_jvmdir}/%{jredir}/lib/security/policy/unlimited/US_export_policy.jar
%config(noreplace) %{_jvmdir}/%{jredir}/lib/security/policy/unlimited/local_policy.jar
%config(noreplace) %{_jvmdir}/%{jredir}/lib/security/policy/limited/US_export_policy.jar
%config(noreplace) %{_jvmdir}/%{jredir}/lib/security/policy/limited/local_policy.jar
%config(noreplace) %{_jvmdir}/%{jredir}/lib/security/blacklisted.certs
%{_datadir}/icons/hicolor/*x*/apps/java-%{javaver}-openjdk.png
%{_mandir}/man1/java-%{name}.1*
%{_mandir}/man1/keytool-%{name}.1*
%{_mandir}/man1/orbd-%{name}.1*
%{_mandir}/man1/pack200-%{name}.1*
%{_mandir}/man1/rmid-%{name}.1*
%{_mandir}/man1/rmiregistry-%{name}.1*
%{_mandir}/man1/servertool-%{name}.1*
%{_mandir}/man1/tnameserv-%{name}.1*
%{_mandir}/man1/unpack200-%{name}.1*

%files devel
%defattr(-,root,root,-)
%dir %{_jvmdir}/%{sdkdir}/bin
%dir %{_jvmdir}/%{sdkdir}/include
%dir %{_jvmdir}/%{sdkdir}/lib
%dir %{_jvmdir}/%{sdkdir}/tapset
%{_jvmdir}/%{sdkdir}/bin/*
%{_jvmdir}/%{sdkdir}/include/*
%{_jvmdir}/%{sdkdir}/lib/*
%{_jvmdir}/%{sdkdir}/tapset/*.stp
%{_jvmdir}/%{sdklnk}
%{?_jvmjardir:%{_jvmjardir}/%{sdklnk}}
%{_datadir}/applications/%{name}-jconsole.desktop
%{_datadir}/applications/%{name}-policytool.desktop
%{_mandir}/man1/appletviewer-%{name}.1*
%{_mandir}/man1/extcheck-%{name}.1*
%{_mandir}/man1/idlj-%{name}.1*
%{_mandir}/man1/jar-%{name}.1*
%{_mandir}/man1/jarsigner-%{name}.1*
%{_mandir}/man1/javac-%{name}.1*
%{_mandir}/man1/javadoc-%{name}.1*
%{_mandir}/man1/javah-%{name}.1*
%{_mandir}/man1/javap-%{name}.1*
%{_mandir}/man1/jcmd-%{name}.1*
%{_mandir}/man1/jconsole-%{name}.1*
%{_mandir}/man1/jdeps-%{name}.1*
%{_mandir}/man1/jdb-%{name}.1*
%{_mandir}/man1/jhat-%{name}.1*
%{_mandir}/man1/jinfo-%{name}.1*
%{_mandir}/man1/jjs-%{name}.1*
%{_mandir}/man1/jmap-%{name}.1*
%{_mandir}/man1/jps-%{name}.1*
%{_mandir}/man1/jrunscript-%{name}.1*
%{_mandir}/man1/jsadebugd-%{name}.1*
%{_mandir}/man1/jstack-%{name}.1*
%{_mandir}/man1/jstat-%{name}.1*
%{_mandir}/man1/jstatd-%{name}.1*
%{_mandir}/man1/native2ascii-%{name}.1*
%{_mandir}/man1/policytool-%{name}.1*
%{_mandir}/man1/rmic-%{name}.1*
%{_mandir}/man1/schemagen-%{name}.1*
%{_mandir}/man1/serialver-%{name}.1*
%{_mandir}/man1/wsgen-%{name}.1*
%{_mandir}/man1/wsimport-%{name}.1*
%{_mandir}/man1/xjc-%{name}.1*
%{tapsetdir}/*.stp

%files demo -f %{name}-demo.files
%defattr(-,root,root,-)

%files src
%defattr(-,root,root,-)
%doc README.src
%{_jvmdir}/%{sdkdir}/src.zip

%files javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/%{name}

%changelog
* Sat Nov 02 2024 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.33.0-1
- Update to 3.33.0

* Sat Jul 27 2024 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.32.0-1
- Update to 3.32.0

* Sat Apr 20 2024 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.31.0-1
- Update to 3.31.0

* Thu Feb 01 2024 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.30.0-1
- Update to 3.30.0

* Wed Oct 25 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.29.0-1
- Update to 3.29.0

* Thu Jul 27 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.28.0-1
- Update to 3.28.0

* Fri Apr 28 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.27.0-1
- Update to 3.27.0

* Sun Feb 05 2023 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.26.0-1
- Update to 3.26.0

* Fri Nov 25 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.25.0-1
- Update to 3.25.0

* Thu Jul 28 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.24.0-1
- Update to 3.24.0

* Sun Jun 26 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.23.0-1
- Update to 3.23.0

* Fri Mar 04 2022 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.22.0-1
- Update to 3.22.0 and adapt to Git tarballs

* Mon Nov 01 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.21.0-2
- Remove xorg-x11-utils requirement on Fedora 36+.

* Mon Nov 01 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.21.0-1
- Update to 3.21.0

* Wed Jul 28 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.20.0-0
- Update to 3.20.0

* Mon May 03 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.19.0-0
- Update to 3.19.0.

* Fri Feb 05 2021 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.18.0-0
- Update to 3.18.0.
- Drop unneeded libXdmcp-devel dependency.
- Require LCMS >= 2.11 (current in-tree version) to use system LCMS.

* Thu Nov 26 2020 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.17.1-1
- Replace haveshenandoah with shenandoah_arches as in the RHEL build.
- Catch unsupported build architectures and exit with an error.

* Wed Nov 25 2020 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.17.1-0
- Update to 3.17.1.

* Thu Oct 29 2020 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.17.0-2
- Turn off LTO on Fedora so libjvm.so doesn't fail to link.

* Tue Oct 27 2020 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.17.0-2
- Update to 3.17.0.
- Enable JFR on all JIT architectures now JDK-8252096/PR3810 is fixed for x86.
- Disable pre-compiled headers on AArch64 again now build breakage is fixed.

* Mon Oct 26 2020 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.17.0-1
- Update to 3.17.0pre02.
- Disable JFR explicitly on architectures where it doesn't build (x86).
- Enable pre-compiled headers on AArch64 due to current breakage without.

* Mon Aug 24 2020 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.17.0-0
- Update to 3.17.0pre01.

* Sat May 02 2020 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.16.0-1
- Update to 3.16.0.

* Sun Apr 19 2020 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.16.0-0
- Update to 3.16.0pre01.

* Mon Jan 20 2020 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.15.0-1
- Update to 3.15.0.

* Tue Dec 24 2019 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.15.0-0
- Update to 3.15.0pre01.

* Tue Nov 12 2019 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.14.0-1
- Update to 3.14.0.

* Tue Nov 12 2019 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.14.0-1
- Turn off 'haveshenandoah' on all architectures so the IcedTea HotSpot gets fully tested.

* Thu Oct 17 2019 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.14.0-0
- Update to 3.14.0pre01.

* Thu Jul 18 2019 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.13.0-1
- Update to 3.13.0.

* Wed Jul 17 2019 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.13.0-0
- Update to 3.13.0pre01.

* Wed May 01 2019 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.12.0-2
- Bump AArch32 changeset to switch to upstream version (jdk8u212-b04-aarch32-190430).

* Tue Apr 30 2019 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.12.0-1
- Bump AArch32 changeset to pick up 8214189.

* Mon Apr 29 2019 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.12.0-1
- Bump AArch32 changeset to pick up 8213419.

* Sun Apr 28 2019 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.12.0-1
- Update to 3.12.0.

* Wed Apr 17 2019 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.12.0-0
- Update to 3.12.0pre01.

* Thu Feb 28 2019 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.11.0-3
- Update to 3.11.0.

* Mon Feb 04 2019 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.11.0-2
- Bump Shenandoah & AArch32 changesets for 3.11.0pre02.

* Thu Jan 24 2019 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.11.0-1
- Bump HotSpot changeset to pick up PR3683.

* Wed Jan 23 2019 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.11.0-1
- Update to 3.11.0pre02.

* Tue Jan 15 2019 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.11.0-0
- Remove SunEC+NSS logic following PR3667.

* Mon Jan 14 2019 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.11.0-0
- Update to 3.11.0pre01.

* Sun Dec 23 2018 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.10.0-1
- Update to 3.10.0

* Sat Dec 01 2018 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.10.0-0
- Setup architecture definitions for non-JIT archs after generic no-JIT section so it doesn't override them.
- Turn off Shenandoah on ppc64le and add a note about it being enabled for testing on s390 and ppc64be.

* Sat Dec 01 2018 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.10.0-0
- Introduce stapinstall variable to set SystemTap arch directory correctly (e.g. arm64 on aarch64)
- Remove cacerts and tapset symlink creation now handled by IcedTea's install phase.

* Thu Nov 22 2018 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.10.0-0
- Add '-openjdk' suffix to icon files, following PR3624.

* Wed Nov 21 2018 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.10.0-0
- Update to 3.10.0pre01.

* Thu Sep 13 2018 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.9.0-2
- Temporarily turn on Shenandoah on s390 & ppc64 to test PR3619, PR3620 & PR3623.

* Thu Sep 13 2018 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.9.0-2
- Remove unused archbuild & archinstall and add missing ppc64le & s390 archs.

* Thu Sep 13 2018 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.9.0-2
- Update to 3.9.0.

* Sat Sep 01 2018 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.9.0-1
- Update to 3.9.0pre02.

* Tue Aug 14 2018 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.9.0-0
- Update to 3.9.0pre01.

* Sun May 27 2018 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.8.0-3
- Update to 3.8.0.

* Wed May 16 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.8.0-2
- Turn on -Werror and filter out additional warnings introduced by RPM build flags.

* Mon May 14 2018 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.8.0-1
- Fix OpenJDK changeset/checksum to match final version of pre02.

* Mon May 14 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.8.0-1
- Restrict use of OpenJDK 7 to bootstrap to RHEL 7 and earlier.

* Mon May 14 2018 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.8.0-1
- Update to 3.8.0pre02.

* Mon Mar 26 2018 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.8.0-0
- Update to 3.8.0pre01.

* Wed Feb 28 2018 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.7.0-3
- Update AArch32 changeset to jdk8u161-b13-aarch32-180220.

* Mon Feb 26 2018 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.7.0-2
- Update HotSpot changesets to versions with fixed version of 8164113.

* Fri Feb 23 2018 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.7.0-2
- Update to 3.7.0.

* Mon Jan 29 2018 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.7.0-1
- Handle removal of _jvmjardir on recent versions of Fedora.

* Wed Jan 24 2018 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.7.0-0
- Update to 3.7.0pre01.

* Wed Nov 01 2017 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.6.0-1
- Update location of policy JAR files following 8157561.

* Wed Nov 01 2017 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.6.0-1
- Update to 3.6.0.

* Mon Oct 30 2017 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.6.0-0
- Update to 3.6.0pre02.

* Fri Jul 28 2017 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.5.1-0
- Bump shenandoah to aarch64-shenandoah-jdk8u141-b16-shenandoah-merge-2017-07-27-02.

* Thu Jul 27 2017 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.5.1-0
- Update to 3.5.1.

* Thu Jul 20 2017 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.5.0-1
- Update to 3.5.0.

* Fri Jul 07 2017 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.5.0-0
- Update to 3.5.0pre01.

* Tue May 16 2017 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.4.0-2
- Use AArch32 port version for faster bootstrap.
- Require Perl for building (used in javac.in).

* Thu May 11 2017 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.4.0-2
- Add AArch32 port support.

* Wed May 10 2017 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.4.0-1
- Update to 3.4.0.
- Define haveshenandoah and enable for x86_64 and aarch64.

* Tue May 09 2017 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.4.0-0
- Update to 3.4.0pre01.

* Mon Feb 06 2017 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.3.0-2
- Turn on improved font rendering and add fontconfig-devel dependency.
- Depend on zip which is not automatically pulled in on RHEL 6.
- Use auto-detection to pick up bootstrap JVM.
- Handle arch suffix used in JDK naming on RHEL 6.
- Remove build requirement on wget, as we do not download during build.

* Wed Jan 25 2017 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.3.0-2
- Update to 3.3.0.

* Tue Jan 24 2017 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.3.0-1
- Update to 3.3.0pre02.

* Fri Jan 13 2017 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.3.0-0
- Update to 3.3.0pre01.

* Tue Nov 08 2016 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.2.0-3
- Update to 3.2.0.

* Mon Nov 07 2016 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.2.0-2
- Update to 3.2.0pre03.
- Add Kerberos, SCTP and PCSC build dependencies for new features
- Disable pre-compiled headers.

* Mon Aug 08 2016 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.2.0-1
- Remove unused variables sa_arches, no_prelink_arches and no6_arches.
- Use !jit_arches rather than zero_arches, removing the latter.

* Mon Aug 08 2016 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.2.0-1
- Update to 3.2.0pre02.

* Thu Aug 04 2016 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.2.0-0
- Update to 3.2.0pre01.

* Tue Jul 26 2016 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.1.0-4
- Update to 3.1.0.

* Mon Jul 25 2016 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.1.0-3
- Update to 3.1.0pre04, turning on Shenandoah on x86_64.

* Mon Jul 25 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.1.0-2
- Run make check, turning off long-running JTreg tests and broken SystemTap tests.

* Fri Jul 15 2016 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.1.0-2
- Update to 3.1.0pre03.

* Fri May 20 2016 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.1.0-1
- Update to 3.1.0pre02.

* Mon May 16 2016 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.1.0-0
- Update to 3.1.0pre01.

* Fri Apr 08 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.0.0-5
- Update handling of desktop files, following addition of version by IcedTea.

* Fri Apr 08 2016 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.0.0-5
- Add build dependency on libXcomposite-devel.

* Fri Apr 08 2016 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.0.0-5
- Update to 3.0.0.

* Tue Feb 23 2016 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.0.0-4
- Update to 3.0.0pre09.

* Fri Jan 29 2016 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.0.0-3
- Update to 3.0.0pre08.

* Wed Dec 23 2015 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.0.0-3
- Drop unneeded accessibility and execstack requirements
- Reduce redhat-lsb requirement to redhat-lsb-core (we just need lsb_release)
- Fix use of variable in comment

* Tue Dec 22 2015 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.0.0-2
- Update to 3.0.0pre07.

* Wed Sep 16 2015 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.0.0-1
- Allow bootstrap JDK to be java-1.8.0-openjdk on Fedora 21 and above.

* Wed Sep 16 2015 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.0.0-1
- Update to 3.0.0pre05.

* Fri Jun 19 2015 Andrew Hughes <gnu.andrew@redhat.com> - 1:3.0.0-0
- Remove conditionals around tapset rules as they are always present in IcedTea
- Fix Nashorn URL
- Override more configure paths to ensure correct installation
- Set LDFLAGS empty until PR2428 is fixed
- Drop permission change to sa-jdi.jar as no longer needed.
- Bring back SystemTap symlink installation.
- Create directory for man pages and remove the IcedTea installed directory afterwards.
- Do execstack call using existence test, not an arch test.
- Point RPM to docs installed by IcedTea rather than installing its own.
- Install release and blacklisted.certs
- Fix path of icons installed by IcedTea.
- Drop apt man page and add ones for jdeps and jjs.

* Mon Jun 08 2015 Andrew John Hughes <gnu.andrew@redhat.com> - 1:3.0.0-0
- Update to 3.0.0pre04.

* Wed Jun 03 2015 Andrew John Hughes <gnu.andrew@redhat.com> - 1:2.6.0-10
- Update to 2.6.0pre21.

* Tue Jun 02 2015 Andrew John Hughes <gnu.andrew@redhat.com> - 1:2.6.0-9
- Always depend on nss-devel as it provides nss.pc

* Tue Jun 02 2015 Andrew John Hughes <gnu.andrew@redhat.com> - 1:2.6.0-9
- Change no bootstrap JDK to java-1.7.0-openjdk-devel

* Tue Jun 02 2015 Andrew John Hughes <gnu.andrew@redhat.com> - 1:2.6.0-9
- Avoid doing a full bootstrap on Zero architectures due to timeout

* Tue Jun 02 2015 Andrew John Hughes <gnu.andrew@redhat.com> - 1:2.6.0-9
- Generalise architectures without OpenJDK 6 to no6_arches

* Mon Jun 01 2015 Andrew John Hughes <gnu.andrew@redhat.com> - 1:2.6.0-9
- Update to 2.6.0pre20.

* Fri Dec 19 2014 Andrew Hughes <gnu.andrew@redhat.com> - 1:2.6.0-8
- Add conditional dependencies and build options to allow builds on RHEL 6.

* Fri Dec 12 2014 Andrew John Hughes <gnu.andrew@redhat.com> - 1:2.6.0-7
- Update to 2.6.0pre15.

* Tue Nov 11 2014 Andrew John Hughes <gnu.andrew@redhat.com> - 1:2.6.0-6
- Update to 2.6.0pre11.
- No more need for AArch64-specific tarballs.

* Fri Nov 07 2014 Andrew John Hughes <gnu.andrew@redhat.com> - 1:2.6.0-5
- Update to 2.6.0pre10.

* Fri Nov 07 2014 Andrew Hughes <gnu.andrew@redhat.com> - 1:2.6.0-4
- Use java-1.7.0-openjdk for AArch64 as it does not have 1.6.
- Update to use --prefix option to configure instead of arch-install-dir.
- Drop --enable-nss and obsolete --enable-pulse-java.

* Fri Oct 31 2014 Andrew John Hughes <gnu.andrew@redhat.com> - 1:2.6.0-4
- Update to 2.6.0pre09.

* Tue Sep 16 2014 Andrew John Hughes <gnu.andrew@redhat.com> - 1:2.6.0-3
- Use /usr/lib/jvm/java-1.6.0 until java-1.6.0-openjdk is provided (RH1143771)
- Include icedteasnapshot in tarball extraction name

* Tue Sep 16 2014 Andrew John Hughes <gnu.andrew@redhat.com> - 1:2.6.0-3
- Explicitly pass paths to bootstrap JDKs
- Handle non-Fedora/RHEL builds with havegcj.

* Tue Sep 16 2014 Andrew John Hughes <gnu.andrew@redhat.com> - 1:2.6.0-3
- Update to 2.6.0pre08.

* Tue Sep 16 2014 Andrew John Hughes <gnu.andrew@redhat.com> - 1:2.5.2-1
- Adapt to work on RHEL 7.

* Tue Sep 16 2014 Andrew John Hughes <gnu.andrew@redhat.com> - 1:2.5.2-1
- Use correct changesets and fix AArch64 URL.

* Tue Sep 16 2014 Andrew John Hughes <gnu.andrew@redhat.com> - 1:2.5.2-1
- Update to 2.5.2 and use new URLs.

* Thu May 15 2014 Andrew John Hughes <gnu.andrew@redhat.com> - 1:2.6pre04-2
- Support ppc64le JIT

* Mon May 12 2014 Andrew John Hughes <gnu.andrew@redhat.com> - 1:2.6pre04-1
- Allow builds on rawhide with SunEC provider

* Wed Apr 16 2014 Andrew John Hughes <gnu.andrew@redhat.com> - 1:2.4.7-1
- Update to 2.4.7

* Thu Mar 27 2014 Andrew John Hughes <gnu.andrew@redhat.com> - 1:2.4.6-1
- Adapt to 2.4.6
- Remove accessibility and OpenJDK 6 definitions
- Add aarch64 definitions
- Add aarch64 to jit_arches
- Define sa_arches as jit_arches excluding aarch64
- Define noprelink_arches as aarch64
- Drop systemtap option
- Use different HotSpot tarball for aarch64
- Enable the ARM32 JIT
- Only depend on prelink for archs not in noprelink_arches
- Only install sa-jdi.jar on sa_arches
- Only run execstack for archs not in prelink_arches
- Add policies to config

* Thu Mar 27 2014 Andrew John Hughes <gnu.andrew@redhat.com> - 1:2.3.14-1
- Adapt to 2.3.14
- Bootstrap using native ecj from gcj, to avoid buggy versions on recent Fedoras
- Drop all patches, including outdated accessibility layer
- Add new forest changeset IDs and URLs
- Depend on lcms2 and libattr-devel
- Only depend on ant-nodeps on F19 and older
- Use java-1.6.0-icedtea-devel for non-bootstrap builds
- Remove ExclusiveArch restriction
- Obsolete old java-1.x.0-openjdk packages
- Add jcmd binary and man page
- Fix path to TRADEMARK file
- Remove java.security.old (not in 2.x) and add nss.cfg as config file

* Mon Mar 24 2014 Andrew John Hughes <gnu.andrew@redhat.com> - 1:1.13.1-1
- Make package buildable on F16/17
- Turn on gcj bootstrap
- Use upstream OpenJDK tarball
- Split systemtap option from bootstrap option
- Change name to IcedTea
- Fix versioning
- Drop unneeded patch name prefixing
- Backport build fixes from 1.13 branch (system LCMS and -Werror)
- Add missing build requirements, based on Gentoo
- Remove VisualVM build requirements
- Drop runtime Rhino requirement
- Add runtime Gtk2 requirement for look-and-feel
- Use configure macro and allow it to detect parallelism itself
- Explicitly turn off downloading and turn on NSS and system Kerberos
- Pass _smp_mflags to make
- Drop unneeded patch-ecj call

* Thu Jan 23 2014 Jiri Vanek <jvanek@redhat.com> - 1:1.6.0.1-3.1.13.0
- updated to icedtea 1.13.1
 - http://blog.fuseyism.com/index.php/2014/01/23/security-icedtea-1-12-8-1-13-1-for-openjdk-6-released/
- updated to jdk6, b30,  21_jan_2014
 - https://openjdk6.java.net/OpenJDK6-B30-Changes.html
- adapted patch7 1.13_fixes.patch
- pre 2011 changelog moved to (till now  wrong) pre-2009-spec-changelog (rh1043611)
- added --disable-system-lcms to configure options to pass build
- adapted patch3 java-1.6.0-openjdk-java-access-bridge-security.patch
- Resolves: rhbz#1050190

* Wed Oct 30 2013 Jiri Vanek <jvanek@redhat.com> - 1:1.6.0.1-1.66.1.13.0
- updated to icedtea 1.13
- updated to openjdk-6-src-b28-04_oct_2013
- added --disable-lcms2 configure switch to fix tck
- removed upstreamed patch7,java-1.6.0-openjdk-jstack.patch
- added patch7 1.13_fixes.patch to fix 1.13 build issues
- adapted patch0 java-1.6.0-openjdk-optflags.patch
- adapted patch3 java-1.6.0-openjdk-java-access-bridge-security.patch
- adapted patch8 java-1.6.0-openjdk-timezone-id.patch
- removed useless runtests parts
- included also java.security.old files
- Resolves: rhbz#1017621

* Wed Sep 04 2013 Omair Majid <omajid@redhat.com> - 1:1.6.0.1-1.65.1.11.13
- added patch8, java-1.6.0-openjdk-timezone-id.patch to 995488
- Resolves: rhbz#983411

* Wed Sep 04 2013 Jiri Vanek <jvanek@redhat.com> - 1:1.6.0.0-1.63.1.11.13
- removed upstreamed  patch100  8000791-regression-fix.patch
- bumped release
- updated to icedtea-1.11.13
- Resolves: rhbz#983411

* Thu Jun 27 2013 Jiri Vanek <jvanek@redhat.com> - 1:1.6.0.0-1.63.1.11.11.90
- added patch100  8000791-regression-fix.patch
- bumped release
- updated to icedtea-1.11.12
- Resolves: rhbz#976897
- Resolves: rhbz#983411

* Thu Jun 27 2013 Jiri Vanek <jvanek@redhat.com> - 1:1.6.0.0-1.62.1.11.11.90
- updated to icedtea6-1.11.11.90.tar.gz
- removed upstreamed patch9 jaxp-backport-factoryfinder.patch
- removed upstreamed patch10 fixToFontSecurityFix.patch.
- modified patch3, java-1.6.0-openjdk-java-access-bridge-security.patch
- Resolves: rhbz#973130

* Tue Apr 23 2013 Jiri Vanek <jvanek@redhat.com> - 1:1.6.0.0-1.61.1.11.11
- added and applied (temporally) patch10   fixToFontSecurityFix.patch.
 - fixing regression in fonts introduced by one security patch.
- Resolves: rhbz#950387

* Sun Apr 21 2013 Jiri Vanek <jvanek@redhat.com> - 1:1.6.0.0-1.60.1.11.11
- added and applied (temporally) one more patch to xalan/xerces privileges
 - patch9 jaxp-backport-factoryfinder.patch
- will be upstreamed
- Resolves: rhbz#950387

* Fri Apr 19 2013 Jiri Vanek <jvanek@redhat.com> - 1:1.6.0.0-1.59.1.11.11
- Updated to icedtea6 1.11.11 - fixed xalan/xerxes privledges
- removed patch 8 -  removingOfAarch64.patch.patch - fixed upstream
- Resolves: rhbz#950387

* Wed Apr 17 2013 Jiri Vanek <jvanek@redhat.com> - 1:1.6.0.0-1.58.1.11.10 
- Updated to icedtea6 1.11.10
- rewritten java-1.6.0-openjdk-java-access-bridge-security.patch
- excluded aarch64.patch
  - by patch 8 -  removingOfAarch64.patch.patch
- Resolves: rhbz#950387

* Mon Feb 18 2013 Jiri Vanek <jvanek@redhat.com> - 1:1.6.0.0-1.56.1.11.8
- Rebuild with updated sources
- Resolves: rhbz#912256

* Fri Feb 15 2013 Jiri Vanek <jvanek@redhat.com> - 1:1.6.0.0-1.34.1.11.8
- Updated to icedtea6 1.11.8
- Removed patch9   7201064.patch
- Removed patch10   8005615.patch
- Removed  not-applied patch 6664509.patch
- Removed mauve as deadly outdated and run on QA
  -  jtreg kept, useless, but working
- Resolves: rhbz#911525

* Wed Feb 06 2013 Jiri Vanek <jvanek@redhat.com> - 1:1.6.0.0-1.54.1.11.6
- removed patch8 revertTwoWrongSecurityPatches2013-02-06.patch
- added patch8:   7201064.patch to be reverted
- added patch9:   8005615.patch to fix the 6664509.patch
- Resolves: rhbz#906708

* Wed Feb 06 2013 Jiri Vanek <jvanek@redhat.com> - 1:1.6.0.0-1.53.1.11.6
- added patch8 revertTwoWrongSecurityPatches2013-02-06.patch
  to remove   6664509 and 7201064 from 1.11.6 tarball
- Resolves: rhbz#906708

* Mon Feb 04 2013 Jiri Vanek <jvanek@redhat.com> - 1:1.6.0.0-1.51.1.11.6
- Updated to icedtea6 1.11.6
- Rewritten java-1.6.0-openjdk-java-access-bridge-security.patch 
- Access gnome bridge jar is forced to have 644 permissions
- Resolves: rhbz#906708

* Tue Jun 12 2012 Jiri Vanek <jvanek@redhat.com> - 1:1.6.0.0-1.48.1.11.3
- Access gnome bridge jar is forced to have 644 permissions
- Resolves: rhbz#828752

* Sat Jun 09 2012 Jiri Vanek <jvanek@redhat.com> - 1:1.6.0.0-1.47.1.11.3
- Modified patch3, java-1.6.0-openjdk-java-access-bridge-security.patch:
  - com.sun.org.apache.xerces.internal.utils.,com.sun.org.apache.xalan.internal.utils.
  - packages added also to package.definition
- Resolves: rhbz#828752

* Fri Jun 08 2012 Jiri Vanek <jvanek@redhat.com> - 1:1.6.0.0-1.46.1.11.3
- Updated to IcedTea6 1.11.3
- Removed upstreamed patch8 - java-1.6.0-openjdk-jirafix_2820_2821.patch
- Modified patch3, java-1.6.0-openjdk-java-access-bridge-security.patch:
  - com.sun.org.apache.xerces.internal.utils.,com.sun.org.apache.xalan.internal.utils.
  - packages added to patch
- Resolves: rhbz#828752

* Fri May 25 2012 Mark Wielaard <mjw@redhat.com> - 1:1.6.0.0-1.45.1.11.1
- Resolves: rhbz#804632
- Tweak java-1.6.0-openjdk-jstack.patch stack to remove two uses of sprintf
  to make it work against systemtap 1.7.

* Tue Apr 24 2012 Jiri Vanek <jvanek@redhat.com> - 1:1.6.0.0-1.44.1.11.1 
- Applied ptisnovs's patch8
- Resolves: rhbz#807324

* Mon Mar 26 2012 Jiri Vanek <jvanek@redhat.com> - 1:1.6.0.0-1.43.1.11.1 
- Applied Mark's patch7
- Resolves: rhbz#804632

* Mon Mar 19 2012 Mark Wielaard <mjw@redhat.com> - 1:1.6.0.0-1.42.1.11.1
- Resolves: rhbz#804632
- Added patch7 java-1.6.0-openjdk-jstack.patch based on upstream patches:
  http://thread.gmane.org/gmane.comp.java.openjdk.distro-packaging.devel/17667

* Tue Feb 14 2012 Deepak Bhole <dbhole@redhat.com> - 1:1.6.0.0-1.41.1.11.1
- Resolves: rhbz#771971
- Updated to IcedTea6 1.11.1
- Security fixes:
  - S7112642, CVE-2012-0497: Incorrect checking for graphics rendering object
  - S7082299, CVE-2011-3571: AtomicReferenceArray insufficient array type check
  - S7110687, CVE-2012-0503: Unrestricted use of TimeZone.setDefault
  - S7110700, CVE-2012-0505: Incomplete info in the deserialization exception
  - S7110683, CVE-2012-0502: KeyboardFocusManager focus stealing
  - S7088367, CVE-2011-3563: JavaSound incorrect bounds check
  - S7126960, CVE-2011-5035: Add property to limit number of request headers to the HTTP Server
  - S7118283, CVE-2012-0501: Off-by-one bug in ZIP reading code
  - S7110704, CVE-2012-0506: CORBA fix

* Mon Oct 24 2011 Deepak Bhole <dbhole@redhat.com> - 1:1.6.0.0-1.41.1.10.4
- Bump to IcedTea6 1.10.4
- Resolves: rhbz#744789

* Fri Jul 22 2011 Deepak Bhole <dbhole@redhat.com> - 1:1.6.0.0-1.40.1.10.3
- Bump to IcedTea6 1.10.3, HotSpot 20
- Resolves: rhbz#722310

* Fri Jun 10 2011 Jiri Vanek <jvanek@redhat.com> - 1:1.6.0.0-39.1.9.7
- added requires: fontconfig
- resolves: rhbz#708201
