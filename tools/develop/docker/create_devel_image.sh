#!/usr/bin/env bash

ubuntu_version="20.04" # TODO: From program option.

script_dir=$(readlink --canonicalize-existing --verbose                        \
    "$(dirname "$(command -v "$0")")")
readonly script_dir

docker build --tag ccdevel --build-arg "UBUNTU_VERSION=${ubuntu_version}"      \
    ${script_dir}
