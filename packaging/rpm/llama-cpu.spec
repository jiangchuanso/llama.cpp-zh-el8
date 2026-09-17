Name:           llama-cpu
# both defines are passed by .github/workflows/build-rpm.yml
Version:        %{?llama_version}%{!?llama_version:0.0.0}
Release:        1.b%{?llama_build}%{!?llama_build:0}%{?dist}
Summary:        llama.cpp CPU inference server (EL8 / Kylin V10 build)

License:        MIT
URL:            https://github.com/jiangchuanso/llama.cpp-zh-el8
Source0:        llama-server.service
Source2:        README.md
Source3:        llama-cpu-models.ini

# The binaries come prebuilt from the CI `ubuntu` job (rpmbuild/SOURCES/bin).
# They carry libstdc++.so.6 and libgomp.so.1 next to themselves and load them
# through an $ORIGIN rpath, so the C++ runtime belongs to this package. Scanning
# those files would add "libstdc++.so.6(GLIBCXX_3.4.25)(64bit)" to Requires and
# to Provides: Kylin V10 has only GLIBCXX_3.4.24, and a private copy must not
# claim that soname system-wide. Turn the scanner off, declare the real
# dependencies by hand below.
AutoReqProv:    no

# binaries, archives and libraries are shipped exactly as built: do not strip
%global __os_install_post %{nil}

# Thread counts substituted into llama-cpu-models.ini below. Left unset,
# llama-server uses every logical core, which is a bad default on many-core
# hosts: a 128-core Phytium S5000C generates 32.5 t/s with 8 threads but only
# 2.3 t/s with 128. x86_64 has to cover both the Xeon E5-2620 v4 and the Hygon
# C86-3G 5380, whose generation optima differ (32 vs 4 threads), so 16 is the
# compromise; both prefer 32 for batch processing.
%ifarch aarch64
%global preset_threads         8
%global preset_threads_batch  32
%else
%global preset_threads        16
%global preset_threads_batch  32
%endif

Requires:       glibc >= 2.28
Requires:       systemd
Requires(pre):  shadow-utils

%description
Prebuilt CPU-only llama.cpp serving stack for EL8 and compatible systems
(CentOS/Rocky/AlmaLinux 8, Kylin Advanced Server V10).

The binaries and their runtime libraries (including libstdc++ and libgomp) are
bundled under /opt/llama-cpu and loaded through an $ORIGIN rpath, so the package
does not depend on the host C++ runtime version.

A systemd unit (llama-server.service) is installed but not enabled. The default
configuration runs llama-server in router mode: every .gguf found in
/var/lib/llama-cpu/models is registered automatically and models are loaded on
demand. Drop model files into that directory, optionally tune per-model
settings in /etc/llama-cpu/models.ini, then run: systemctl enable --now llama-server

%prep
# nothing to unpack, the prebuilt binaries are used as-is

%build
# nothing to build

%install
rm -rf %{buildroot}
install -d %{buildroot}/opt/llama-cpu/bin
cp -a %{_sourcedir}/bin/. %{buildroot}/opt/llama-cpu/bin/
chmod 0755 %{buildroot}/opt/llama-cpu/bin/*

install -d %{buildroot}%{_bindir}
for b in llama-server llama-cli llama-bench; do
  if [ -x "%{buildroot}/opt/llama-cpu/bin/$b" ]; then
    ln -sf /opt/llama-cpu/bin/$b "%{buildroot}%{_bindir}/$b"
  fi
done

install -d %{buildroot}%{_unitdir}
install -m 0644 %{SOURCE0} %{buildroot}%{_unitdir}/llama-server.service

install -d %{buildroot}%{_sysconfdir}/llama-cpu
sed -e 's/@THREADS@/%{preset_threads}/' \
    -e 's/@THREADS_BATCH@/%{preset_threads_batch}/' \
    %{SOURCE3} > %{buildroot}%{_sysconfdir}/llama-cpu/models.ini
chmod 0644 %{buildroot}%{_sysconfdir}/llama-cpu/models.ini

install -d %{buildroot}%{_docdir}/llama-cpu
install -m 0644 %{SOURCE2} %{buildroot}%{_docdir}/llama-cpu/README.md

install -d %{buildroot}/var/lib/llama-cpu
install -d -m 0750 %{buildroot}/var/lib/llama-cpu/models

%pre
getent group llama-cpu >/dev/null || groupadd -r llama-cpu
getent passwd llama-cpu >/dev/null || \
  useradd -r -g llama-cpu -d /var/lib/llama-cpu -s /sbin/nologin -c "llama.cpp server" llama-cpu
exit 0

%post
%systemd_post llama-server.service

%preun
%systemd_preun llama-server.service

%postun
%systemd_postun_with_restart llama-server.service

%files
%dir /opt/llama-cpu
/opt/llama-cpu/bin
%{_bindir}/llama-*
%dir %{_sysconfdir}/llama-cpu
%config(noreplace) %{_sysconfdir}/llama-cpu/models.ini
%{_unitdir}/llama-server.service
%{_docdir}/llama-cpu/README.md
%dir %attr(0750,llama-cpu,llama-cpu) /var/lib/llama-cpu
%dir %attr(0750,llama-cpu,llama-cpu) /var/lib/llama-cpu/models
