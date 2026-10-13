Name:           llama-cuda
# these defines are passed by .github/workflows/build-cuda-el8.yml
Version:        %{?llama_version}%{!?llama_version:0.0.0}
Release:        1.b%{?llama_build}%{!?llama_build:0}%{?dist}
Summary:        CUDA backend for the llama-cpu package (EL8 / Kylin V10 build)

License:        MIT
URL:            https://github.com/jiangchuanso/llama.cpp-zh-el8
Source0:        README.md

# The files come prebuilt from the CI `cuda` job (rpmbuild/SOURCES/bin): the
# ggml-cuda backend and the CUDA runtime libraries it links. All of them are
# loaded through the $ORIGIN rpath that llama-cpu already uses, so they belong
# in the llama-cpu binary directory and nowhere else. Shipping the runtime here
# saves the host from installing the whole toolkit (several GB) for three
# libraries; the CI job asserts that libcuda.so.1 is never among them, because
# it comes from the host driver.
AutoReqProv:    no

# binaries, archives and libraries are shipped exactly as built: do not strip
%global __os_install_post %{nil}

# rpm drops build-id links under /usr/lib/.build-id, which this package must not
# do: it ships into /opt/llama-cpu only, and there is no debuginfo package to
# point at anyway, the files are prebuilt. The rm is the belt to the macro's
# braces: with __os_install_post emptied above, rpm may still add them.
%global _build_id_links none

# llama-server loads the backend at run time and the backend links libggml-base
# from llama-cpu: both have to come from the same build, hence the exact pin.
# Upgrading therefore means installing both RPMs in one `rpm -Uvh` transaction.
Requires:       llama-cpu = %{version}-%{release}
Requires:       glibc >= 2.28

%description
CUDA backend for the CPU inference server shipped in llama-cpu.

The package carries the ggml-cuda backend library and the CUDA runtime libraries
it links (libcudart, libcublas and libcublasLt). All of them are read from
/opt/llama-cpu/bin, the directory llama-server looks for backends in, so the
only thing the host still has to install is the NVIDIA driver: the server picks
the backend up at startup and offloads layers automatically (--n-gpu-layers
defaults to "auto").

The driver is deliberately left to the host: it provides libcuda.so.1, which
cannot be bundled. This build is CUDA 13.0, so it needs the 580 driver series
(>= 580.65.06); an older 13.x-capable driver usually works too through NVIDIA's
minor version compatibility, but that is not guaranteed. Without a driver or
without a usable GPU the backend is not loaded and the server keeps running on
the CPU.

A host that already has the CUDA runtime installed is unaffected: the copies in
/opt/llama-cpu/bin are found first through the $ORIGIN rpath and stay inside
this package, nothing is written outside /opt/llama-cpu.

The backend is built for Blackwell only (sm_120 and sm_121, that is the RTX 50
series and RTX Pro Blackwell). On an older card there is no cubin and no PTX to
compile, so the backend is not loaded and the server stays on the CPU.

%prep
# nothing to unpack, the prebuilt files are used as-is

%build
# nothing to build

%install
rm -rf %{buildroot}
install -d %{buildroot}/opt/llama-cpu/bin
cp -a %{_sourcedir}/bin/. %{buildroot}/opt/llama-cpu/bin/
chmod 0755 %{buildroot}/opt/llama-cpu/bin/*

install -d %{buildroot}%{_docdir}/llama-cuda
install -m 0644 %{SOURCE0} %{buildroot}%{_docdir}/llama-cuda/README.md

rm -rf %{buildroot}/usr/lib/.build-id

%files
/opt/llama-cpu/bin/libggml-cuda.so*
/opt/llama-cpu/bin/libcu*.so*
%{_docdir}/llama-cuda/README.md
