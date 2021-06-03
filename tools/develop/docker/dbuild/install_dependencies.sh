#!/usr/bin/env bash

declare -a packages_to_install
packages_to_install=(                                                          \
    "doxygen"                                                                  \
    "g++"                                                                      \
    "gcc"                                                                      \
    "git"                                                                      \
    "libldap2-dev"                                                             \
    "libpq-dev"                                                                \
    "libsasl2-dev"                                                             \
    "libsqlite3-dev"                                                           \
    "libssl-dev"                                                               \
    "libthrift-dev"                                                            \
    "make"                                                                     \
    "mc"                                                                       \
    "python3-dev"                                                              \
    "python3-venv"                                                             \
    "thrift-compiler"
)

declare running_ubuntu_codename
running_ubuntu_codename="$(lsb_release --codename --short)"
readonly running_ubuntu_codename
if [[ "${running_ubuntu_codename}" == "focal" ]]; then
    packages_to_install+=(                                                     \
        "clang-11"                                                             \
        "clang-tidy-11"                                                        \
        "clang-tools-11"                                                       \
        "libclang-common-11-dev"                                               \
        "libclang-cpp11"                                                       \
        "libclang-cpp11-dev"                                                   \
        "libclang1-11"                                                         \
        "libssl-dev"                                                           \
        "postgresql-server-dev-12"                                             \
    )
elif [[ "${running_ubuntu_codename}" == "bionic" ]]; then
    packages_to_install+=(                                                     \
        "curl"                                                                 \
        "libssl1.0-dev"                                                        \
        "postgresql-server-dev-10"
    )
else
    echo "Unsupported ubuntu release" 2>&1
    exit 1
fi

# Install packages that necessary for build CodeCompass.
DEBIAN_FRONTEND=noninteractive apt-get install --yes "${packages_to_install[@]}"

# Install specific nodejs.
curl -sL https://deb.nodesource.com/setup_12.x | bash -                        \
    && apt-get install -y nodejs
