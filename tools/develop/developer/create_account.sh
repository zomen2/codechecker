#!/usr/bin/env bash

set -o pipefail
set +e

if [[ -z "${5}" ]]; then
    echo "Mandatory options is not specified." >&2
    exit 1
fi

if [[ -n "${6}" ]]; then
    echo "Too many options." >&2
    usage >&2
    exit 2
fi

declare -r user_id=${1}
declare user_name=${2}
declare -r group_id=${3}
declare group_name=${4}
declare -r shell_program=${5}

declare existing_group_name
if existing_group_name=$(
    getent group "${group_id}" | cut --delim=":" --fields="1"); then
    # The group exists.
    if [[ "${existing_group_name}" != "${group_name}" ]]; then
        echo "WARNING: Specified group (${group_id}) has existed. Group name "\
"${existing_group_name} will be used instead of ${group_name}." >&2
    else
        echo "Group, named  ${group_name} exists. It will be used."
    fi
    group_name="${existing_group_name}"
else
    # Create group.
    if groupadd --gid "${group_id}" "${group_name}" ; then
        echo "Group, named  ${group_name} created."
    else
        exit $?
    fi
fi
unset existing_group_name
readonly group_name

declare existing_user_name
if existing_user_name=$(id --name --user "${user_id}" 2>/dev/null); then
    # The user exists.
    if [[ "${existing_user_name}" != "${user_name}" ]]; then
        echo "WARNING: Specified user (${user_id}) has existed. User name "\
"${existing_user_name} will be use instead of ${user_name}." >&2
        user_name="${existing_user_name}"
    fi
else
    # Create user.
    if useradd --shell "${shell_program}" --create-home --uid "${user_id}"     \
        --gid "${group_id}" "${user_name}"; then
        echo "User, named \"${user_name}\" successfully created."
    else
        exit $?
    fi
fi
unset existing_user_name
readonly user_name

set -e

# Set user group if he have not got yet.
users_groups=$(id --groups "${user_id}")
if ! [[ "${users_groups}" != *"${user_id}"* ]]; then
  usermod --gid "${group_id}" "${user_id}"
fi

# Allow sudo right for the user.
mkdir --parents "/etc/sudoers.d/"                                           && \
echo "${user_name} ALL=(ALL) NOPASSWD: ALL" > "/etc/sudoers.d/${user_name}" && \
chmod 0440 "/etc/sudoers.d/${user_name}"

