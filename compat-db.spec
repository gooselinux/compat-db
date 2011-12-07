%define db42_version 4.2.52
%define db43_version 4.3.29
%define db4_versions %{db42_version} %{db43_version}

%define _libdb_a	libdb-${soversion}.a
%define _libcxx_a	libdb_cxx-${soversion}.a

Summary: The Berkeley DB database compatibility library
Name: compat-db
Version: 4.6.21
Release: 15%{?dist}
Source0: http://download.oracle.com/berkeley-db/db-%{db42_version}.tar.gz
Source1: http://download.oracle.com/berkeley-db/db-%{db43_version}.tar.gz

Patch1: compat-db-ac_config.patch
Patch3: db-4.5.20-sparc64.patch

# Upstream db-4.2.52 patches
Patch10: http://www.oracle.com/technology/products/berkeley-db/db/update/%{db42_version}/patch.%{db42_version}.1
Patch11: http://www.oracle.com/technology/products/berkeley-db/db/update/%{db42_version}/patch.%{db42_version}.2
Patch12: http://www.oracle.com/technology/products/berkeley-db/db/update/%{db42_version}/patch.%{db42_version}.3
Patch13: http://www.oracle.com/technology/products/berkeley-db/db/update/%{db42_version}/patch.%{db42_version}.4
Patch14: http://www.oracle.com/technology/products/berkeley-db/db/update/%{db42_version}/patch.%{db42_version}.5

# Upstream db-4.3.29 patches
Patch20: http://www.oracle.com/technology/products/berkeley-db/db/update/%{db43_version}/patch.%{db43_version}.1

URL: http://www.oracle.com/database/berkeley-db/
License: BSD
Group: System Environment/Libraries
BuildRequires: findutils, libtool, perl, sed, ed
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires: compat-db42%{?_isa} = %{db42_version}-%{release}
Requires: compat-db43%{?_isa} = %{db43_version}-%{release}

%description
The Berkeley Database (Berkeley DB) is a programmatic toolkit that provides
embedded database support for both traditional and client/server applications.
This package contains various versions of Berkeley DB which were included in
previous releases of Red Hat Linux.

%package -n compat-db42
Summary: The Berkeley DB database %{db42_version} compatibility library
Group: System Environment/Libraries
Version: %{db42_version}
Obsoletes: db1, db1-devel
Obsoletes: db2, db2-devel, db2-utils
Obsoletes: db3, db3-devel, db3-utils
Obsoletes: db31, db32, db3x
Obsoletes: db4 < 4.2, db4-devel < 4.2, db4-utils < 4.2, db4-tcl < 4.2, db4-java < 4.2
Obsoletes: compat-db < 4.6.21-5

%description -n compat-db42
The Berkeley Database (Berkeley DB) is a programmatic toolkit that provides
embedded database support for both traditional and client/server applications.
This package contains Berkeley DB library version %{db42_version} used for compatibility.

%package -n compat-db43
Summary: The Berkeley DB database %{db43_version} compatibility library
Group: System Environment/Libraries
Version: %{db43_version}
Obsoletes: db1, db1-devel
Obsoletes: db2, db2-devel, db2-utils
Obsoletes: db3, db3-devel, db3-utils
Obsoletes: db31, db32, db3x
Obsoletes: db4 < 4.3, db4-devel < 4.3, db4-utils < 4.3, db4-tcl < 4.3, db4-java < 4.3
Obsoletes: compat-db < 4.6.21-5

%description -n compat-db43
The Berkeley Database (Berkeley DB) is a programmatic toolkit that provides
embedded database support for both traditional and client/server applications.
This package contains Berkeley DB library version %{db43_version} used for compatibility.

%prep
%setup -q -c -a 1

%patch1 -p1 -b .ac_config

pushd db-%{db42_version}
%patch10 -p0
%patch11 -p0
%patch12 -p0
%patch13 -p0
%patch14 -p0
popd

pushd db-%{db43_version}
%patch20 -p0
%patch3 -p1 -b .sparc64
popd

pushd db-%{db42_version}/dist
libtoolize --copy --force
for i in `ls aclocal/*.m4`; do
  mv $i `echo $i | sed s/m4$/ac/`
done
popd

mkdir docs
for version in %{db4_versions} ; do
	mkdir docs/db-${version}
	install -m644 db*${version}/{README,LICENSE} docs/db-${version}
done

%build
export CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing"
for version in %{db4_versions} ; do
	pushd db-${version}/dist
	./s_config
	mkdir build_unix
	cd build_unix
	ln -s ../configure
	%configure --prefix=%{_prefix} \
		--enable-compat185 \
		--enable-shared --disable-static \
		--enable-rpc \
		--enable-cxx
	soversion=`echo ${version} | cut -f1,2 -d.`
	make libdb=%{_libdb_a} libcxx=%{_libcxx_a} %{?_smp_mflags}
	popd
done

# remove dangling tags symlink from examples.
rm -f examples_cxx/tags
rm -f examples_c/tags

%install
rm -rf ${RPM_BUILD_ROOT}
mkdir -p ${RPM_BUILD_ROOT}%{_bindir}
mkdir -p ${RPM_BUILD_ROOT}%{_libdir}

for version in %{db4_versions} ; do
	pushd db-${version}/dist/build_unix
	%makeinstall libdb=%{_libdb_a} libcxx=%{_libcxx_a}
	# Move headers to special directory to avoid conflicts
	mkdir -p ${RPM_BUILD_ROOT}%{_includedir}/db${version}
	mv db.h db_185.h db_cxx.h ${RPM_BUILD_ROOT}%{_includedir}/db${version}
	# Rename the utilities.
	major=`echo ${version} | cut -c1,3`
	for bin in ${RPM_BUILD_ROOT}%{_bindir}/*db_* ; do
		t=`echo ${bin} | sed "s,db_,db${major}_,g"`
		mv ${bin} ${t}
	done
	popd
done

# Nuke non-versioned symlinks and headers
rm -f ${RPM_BUILD_ROOT}%{_libdir}/libdb-4.so \
${RPM_BUILD_ROOT}%{_libdir}/libdb.so \
${RPM_BUILD_ROOT}%{_libdir}/libdb_cxx-4.so \
${RPM_BUILD_ROOT}%{_libdir}/libdb_cxx.so \
${RPM_BUILD_ROOT}%{_includedir}/db.h \
${RPM_BUILD_ROOT}%{_includedir}/db_185.h \
${RPM_BUILD_ROOT}%{_includedir}/db_cxx.h


# Make sure all shared libraries have the execute bit set.
chmod 755 ${RPM_BUILD_ROOT}%{_libdir}/libdb*.so*

# XXX Avoid Permission denied. strip when building as non-root.
chmod u+w ${RPM_BUILD_ROOT}%{_bindir} ${RPM_BUILD_ROOT}%{_bindir}/*

# Make %{_libdir}/db<version>/libdb.so symlinks to ease detection for autofoo
for version in %{db4_versions} ; do
	mkdir -p ${RPM_BUILD_ROOT}/%{_libdir}/db${version}
	pushd ${RPM_BUILD_ROOT}/%{_libdir}/db${version}
	ln -s ../../../%{_lib}/libdb-`echo ${version} | cut -b 1-3`.so libdb.so
	ln -s ../../../%{_lib}/libdb_cxx-`echo ${version} | cut -b 1-3`.so libdb_cxx.so
	popd
done


# On Linux systems, move the shared libraries to lib directory.
%ifos linux
if [ "%{_libdir}" != "%{_lib}" ]; then
	mkdir -p ${RPM_BUILD_ROOT}/%{_lib}
	mv ${RPM_BUILD_ROOT}%{_libdir}/libdb*?.?.so* ${RPM_BUILD_ROOT}/%{_lib}/
fi
%endif

# Remove unpackaged files.
rm -fr ${RPM_BUILD_ROOT}%{_libdir}/*.a
rm -fr ${RPM_BUILD_ROOT}%{_libdir}/*.la
rm -fr ${RPM_BUILD_ROOT}%{_prefix}/docs/

%clean
rm -rf ${RPM_BUILD_ROOT}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)

%files -n compat-db42
%doc docs/db-%{db42_version}
%{_bindir}/db42*
%{_bindir}/berkeley_db42_svc
%ifos linux
/%{_lib}/libdb-4.2.so
/%{_lib}/libdb_cxx-4.2.so
%else
%{_libdir}/libdb-4.2.so
%{_libdir}/libdb_cxx-4.2.so
%endif
%{_libdir}/db%{db42_version}
%{_includedir}/db%{db42_version}

%files -n compat-db43
%doc docs/db-%{db43_version}
%{_bindir}/db43*
%{_bindir}/berkeley_db43_svc
%ifos linux
/%{_lib}/libdb-4.3.so
/%{_lib}/libdb_cxx-4.3.so
%else
%{_libdir}/libdb-4.3.so
%{_libdir}/libdb_cxx-4.3.so
%endif
%{_libdir}/db%{db43_version}
%{_includedir}/db%{db43_version}

%changelog
* Fri Jun 02 2010 Jindrich Novy <jnovy@redhat.com> 4.6.21-15
- add -fno-strict-aliasing (#599376)

* Tue May 25 2010 Jindrich Novy <jnovy@redhat.com> 4.6.21-14
- pull in correct compat-dbs on multiarch systems (#589637)

* Wed May 19 2010 Jindrich Novy <jnovy@redhat.com> 4.6.21-13
- fix dependencies in the main package

* Tue May 18 2010 Jindrich Novy <jnovy@redhat.com> 4.6.21-12
- readd 4.2 and 4.3 back for RHEL4/5 compatibility, remove 4.5, 4.6 (#588589)

* Mon Jan 11 2010 Jindrich Novy <jnovy@redhat.com> 4.6.21-11
- apply compatibility patch
- define default file attributes
Related: #543948

* Thu Sep 10 2009 Jindrich Novy <jnovy@redhat.com> 4.6.21-10
- remove libtool hacks so that compat-db builds again
- remove support for old BDBs: 4.3.29, 4.2.52, 4.1.25

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.6.21-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.6.21-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Dec 23 2008 Jindrich Novy <jnovy@redhat.com> 4.6.21-7
- replication clients should be able to open a sequence (upstream bz#16406)

* Wed Nov 12 2008 Jindrich Novy <jnovy@redhat.com> 4.6.21-6
- add old BDBs 4.3.29, 4.2.52, 4.1.25 for third party software compatibility

* Fri Oct 24 2008 Jindrich Novy <jnovy@redhat.com> 4.6.21-5
- drop support for 4.3.29
- split compat-db to compat-db45 and compat-db46 subpackages
  to avoid dependency bloat (#459710)

* Tue Sep 16 2008 Jindrich Novy <jnovy@redhat.com> 4.6.21-4
- build also if db4 is not installed (thanks to Michael A. Peters)

* Sat Aug 02 2008 Jindrich Novy <jnovy@redhat.com> 4.6.21-3
- fix URL to 4.3.29 patch
- official upstream tarball for db-4.3.29 has changed, the only change
  is in license text that allows dual licensing of skiplist.[ch] from
  LGPL to BSD

* Fri Jul 11 2008 Panu Matilainen <pmatilai@redhat.com> 4.6.21-2
- fix broken devel library symlinks

* Wed Jul 09 2008 Jindrich Novy <jnovy@redhat.com> 4.6.21-1
- move db-4.6.21 to compat-db (#449741)
- remove db-4.2.52
- package db46_codegen
- create symlinks to ease detection for autofoo
- fix license and filelists

* Mon Feb 25 2008 Jindrich Novy <jnovy@redhat.com> 4.5.20-5
- manual rebuild because of gcc-4.3 (#434183)

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 4.5.20-4
- Autorebuild for GCC 4.3

* Sat Aug 18 2007 Jindrich Novy <jnovy@redhat.com> 4.5.20-3
- remove db4 provides to workaround RPM obsoletes/provides problem (#111071),
  automatic library provides should be enough for compat-db
- obsolete old db4s again

* Fri Aug 17 2007 Jindrich Novy <jnovy@redhat.com> 4.5.20-2
- fix self-obsoletion

* Mon Jul 30 2007 Jindrich Novy <jnovy@redhat.com> 4.5.20-1
- add 4.5.20 to compat-db
- package db45_hotbackup
- correct open() calls so that compat-db compiles with the new glibc
- apply db185 patches to all compat-db db4s

* Sun Nov 26 2006 Jindrich Novy <jnovy@redhat.com> 4.3.29-2
- include also headers for db4-4.2.52
- sync db4 and compat-db licenses to BSD-style as the result of
  consultation with legal department
- BuildPreReq -> BuildRequires, rpmlint fixes

* Fri Nov 10 2006 Jindrich Novy <jnovy@redhat.com> 4.3.29-1
- add 4.3.29 and remove 4.1.25
- spec reduction diet, remove old unapplied patches
- apply patches 3-5 with upstream fixes for 4.2.52
- apply first upstream fix patch for 4.3.29
- all patches/sources now point to correct URLs
- ship headers for db-4.3.29

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 4.2.52-5.1
- rebuild

* Mon Jul 10 2006 Jindrich Novy <jnovy@redhat.com> 4.2.52-5
- package libdb_cxx, which is a dependency for OpenOffice.org-1.x and
  other legacy software (#198130), thanks to Sivasankar Chander
  <siva.chander@gmail.com>

* Tue Feb 14 2006 Jindrich Novy <jnovy@redhat.com> 4.2.52-4
- clarify pointer usage in db_load.c (#110697)

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 4.2.52-3.2.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 4.2.52-3.2
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Wed Oct 12 2005 Karsten Hopp <karsten@redhat.de> 4.2.52-3
- add Buildprereq ed (#163025)

* Tue Nov 16 2004 Jeff Johnson <jbj@redhat.com> 4.2.52-2
- link libdb-4.1.so against -lpthread (#114150).
- link libdb-4.2.so against -lpthread (#139487).

* Thu Nov 11 2004 Jeff Johnson <jbj@jbj.org> 4.2.52-1
- apply patch.4.1.25.2.
- retire db-4.2.52 with patch.4.2.52.{1,2} into compat-db.
- nuke db2 and db-3.3.11.
- nuke db1 as well.

* Mon Sep 13 2004 Bill Nottingham <notting@redhat.com>
- return of db1 to compat-db
- remove: db-3.1, db-3.2
- remove: c++, tcl sublibraries

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Dec 11 2003 Jeff Johnson <jbj@jbj.org> 4.1.25-1
- retire db-4.1.25 to compat-db.

* Mon Dec 08 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- rebuild for new tcl

* Thu Aug 21 2003 Nalin Dahyabhai <nalin@redhat.com> 4.0.14-6
- rebuild

* Tue Aug 19 2003 Nalin Dahyabhai <nalin@redhat.com> 4.0.14-5
- add missing tcl-devel buildrequires (#101814)

* Thu Jun 26 2003 Jeff Johnson <jbj@redhat.com> 4.0.14-3
- compile on all platforms, use gcc296 only on i386/alpha/ia64
- avoid ppc64 toolchain for the nonce.

* Wed May  7 2003 Bill Nottingham <notting@redhat.com> 4.0.14-2
- build db-4.x with system compiler, not compat-gcc

* Mon May  5 2003 Jeff Johnson <jbj@redhat.com> 4.0.14-1
- add db4.0.14 to the mess.

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Tue Nov 19 2002 Nalin Dahyabhai <nalin@redhat.com> 3.3.11-3
- add sed as a built-time dependency

* Wed Sep 25 2002 Nalin Dahyabhai <nalin@redhat.com>
- fold x86-64 changes into mainline

* Mon Sep 09 2002 Tim Powers <timp@redhat.com>
- x86-64 specific build

* Sun May 26 2002 Tim Powers <timp@redhat.com> 3.3.11-2
- automated rebuild

* Thu May 16 2002 Nalin Dahyabhai <nalin@redhat.com> 3.3.11-1
- pull in db 3.3, obsolete db3 and db32 in addition to db31
- build with compat-gcc/compat-gcc-c++ to get C++ shared libraries suitable
  for use in applications built with db3-devel on RHL 7.x
- pull in db2, obsolete db2/db2-devel/db3-devel, rename to compat-db
- obsolete db3x

* Thu Mar 28 2002 Nalin Dahyabhai <nalin@redhat.com> 3.2.9-4
- rebuild

* Thu Mar 28 2002 Nalin Dahyabhai <nalin@redhat.com> 3.2.9-3
- don't list the tcl include path before other flags when building libdb_tcl
  3.1.x (tcl is in /usr, so this pulls in /usr/include/db.h, which is wrong)

* Mon Mar 25 2002 Nalin Dahyabhai <nalin@redhat.com> 3.2.9-2
- rebuild

* Mon Mar 25 2002 Nalin Dahyabhai <nalin@redhat.com> 3.2.9-1
- rename to db3x and merge in db 3.1 and db 3.2 compatibility stuffs

* Mon Apr 16 2001 Nalin Dahyabhai <nalin@redhat.com>
- rename to db31, drop the -devel subpackage, merge the -utils package
- remove berkeley_db_svc, libdb_tcl.so (conflicts with current -utils)

* Thu Apr 05 2001 Nalin Dahyabhai <nalin@redhat.com>
- fix URLs in docs for the -utils and -devel subpackages to point to the
  images in the main package's documentation directory (#33328)
- change Copyright: GPL to License: BSDish

* Fri Mar 23 2001 Bill Nottingham <notting@redhat.com>
- turn off --enable-debug

* Tue Dec 12 2000 Jeff Johnson <jbj@redhat.com>
- rebuild to remove 777 directories.

* Sat Nov 11 2000 Jeff Johnson <jbj@redhat.com>
- don't build with --enable-diagnostic.
- add build prereq on tcl.
- default value for %%_lib macro if not found.

* Tue Oct 17 2000 Jeff Johnson <jbj@redhat.com>
- add /usr/lib/libdb-3.1.so symlink to %%files.
- remove dangling tags symlink from examples.

* Mon Oct  9 2000 Jeff Johnson <jbj@redhat.com>
- rather than hack *.la (see below), create /usr/lib/libdb-3.1.so symlink.
- turn off --enable-diagnostic for performance.

* Fri Sep 29 2000 Jeff Johnson <jbj@redhat.com>
- update to 3.1.17.
- disable posix mutexes Yet Again.

* Tue Sep 26 2000 Jeff Johnson <jbj@redhat.com>
- add c++ and posix mutex support.

* Thu Sep 14 2000 Jakub Jelinek <jakub@redhat.com>
- put nss_db into a separate package

* Wed Aug 30 2000 Matt Wilson <msw@redhat.com>
- rebuild to cope with glibc locale binary incompatibility, again

* Wed Aug 23 2000 Jeff Johnson <jbj@redhat.com>
- remove redundant strip of libnss_db* that is nuking symbols.
- change location in /usr/lib/libdb-3.1.la to point to /lib (#16776).

* Thu Aug 17 2000 Jeff Johnson <jbj@redhat.com>
- summaries from specspo.
- all of libdb_tcl* (including symlinks) in db3-utils, should be db3->tcl?

* Wed Aug 16 2000 Jakub Jelinek <jakub@redhat.com>
- temporarily build nss_db in this package, should be moved
  into separate nss_db package soon

* Wed Jul 19 2000 Jakub Jelinek <jakub@redhat.com>
- rebuild to cope with glibc locale binary incompatibility

* Wed Jul 12 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Sun Jun 11 2000 Jeff Johnson <jbj@redhat.com>
- upgrade to 3.1.14.
- create db3-utils sub-package to hide tcl dependency, enable tcl Yet Again.
- FHS packaging.

* Mon Jun  5 2000 Jeff Johnson <jbj@redhat.com>
- disable tcl Yet Again, base packages cannot depend on libtcl.so.

* Sat Jun  3 2000 Jeff Johnson <jbj@redhat.com>
- enable tcl, rebuild against tcltk 8.3.1 (w/o pthreads).

* Tue May 30 2000 Matt Wilson <msw@redhat.com>
- include /lib/libdb.so in the devel package

* Wed May 10 2000 Jeff Johnson <jbj@redhat.com>
- put in "System Environment/Libraries" per msw instructions.

* Tue May  9 2000 Jeff Johnson <jbj@redhat.com>
- install shared library in /lib, not /usr/lib.
- move API docs to db3-devel.

* Mon May  8 2000 Jeff Johnson <jbj@redhat.com>
- don't rename db_* to db3_*.

* Tue May  2 2000 Jeff Johnson <jbj@redhat.com>
- disable --enable-test --enable-debug_rop --enable-debug_wop.
- disable --enable-posixmutexes --enable-tcl as well, to avoid glibc-2.1.3
  problems.

* Mon Apr 24 2000 Jeff Johnson <jbj@redhat.com>
- add 3.0.55.1 alignment patch.
- add --enable-posixmutexes (linux threads has not pthread_*attr_setpshared).
- add --enable-tcl (needed -lpthreads).

* Sat Apr  1 2000 Jeff Johnson <jbj@redhat.com>
- add --enable-debug_{r,w}op for now.
- add variable to set shm perms.

* Sat Mar 25 2000 Jeff Johnson <jbj@redhat.com>
- update to 3.0.55

* Tue Dec 29 1998 Jeff Johnson <jbj@redhat.com>
- Add --enable-cxx to configure.

* Thu Jun 18 1998 Jeff Johnson <jbj@redhat.com>
- Create.
