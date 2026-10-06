Name:           llama-cuda
# these defines are passed by .github/workflows/build-cuda-el8.yml
Version:        %{?llama_version}%{!?llama_version:0.0.0}
Release:        1.b%{?llama_build}%{!?llama_build:0}%{?dist}
Summary:        CUDA backend for the llama-cpu package (EL8 / Kylin V10 build)

License:        MIT
URL:            https://github.com/jiangchuanso/llama.cpp-zh-el8
Source0:        README.md

# The file comes prebuilt from the CI `cuda` job (rpmbuild/SOURCES/bin): the
# ggml-cuda backend. It is loaded through the $ORIGIN rpath that llama-cpu
# already uses, so it belongs in the llama-cpu binary directory and nowhere else.
AutoReqProv:    no

# binaries, archives and libraries are shipped exactly as built: do not strip
%global __os_install_post %{nil}

# llama-server loads the backend at run time and the backend links libggml-base
# from llama-cpu: both have to come from the same build, hence the exact pin.
# Upgrading therefore means installing both RPMs in one `rpm -Uvh` transaction.
Requires:       llama-cpu = %{version}-%{release}
Requires:       glibc >= 2.28

%description
CUDA backend for the CPU inference server shipped in llama-cpu.

The package carries the ggml-cuda backend library. It is read from
/opt/llama-cpu/bin, the directory llama-server looks for backends in, so
installing the package is all that is needed to use the GPU: the server picks the
backend up at startup and offloads layers automatically (--n-gpu-layers defaults
to "auto").

The CUDA runtime is deliberately not part of this package (it is several hundred
MB): the host provides it, which means the CUDA 12.x shared libraries
(libcudart.so.12, libcublas.so.12 - cublas pulls in libcublasLt itself) and the
NVIDIA driver with libcuda.so.1. NVIDIA's rhel8 repository has them, e.g.
cuda-cudart-12-8 and cuda-libraries-12-8. Their library directory has to be
visible to the dynamic loader: if it is not registered system-wide, add it to
/etc/ld.so.conf.d/ and run ldconfig, or copy the libraries next to this backend
in /opt/llama-cpu/bin.

CUDA 12.8 is built for the 570 driver series, an older 12.x driver (525.60.13 or
newer) usually works too through NVIDIA's minor version compatibility, but that
is not guaranteed. Without the CUDA runtime or without a usable GPU the backend
is not loaded and the server keeps running on the CPU.

The backend is built with the upstream default CUDA architecture set, which
covers Maxwell and newer GPUs.

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

%files
/opt/llama-cpu/bin/libggml-cuda.so*
%{_docdir}/llama-cuda/README.md
