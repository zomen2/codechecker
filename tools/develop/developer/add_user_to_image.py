#!/usr/bin/env python3

import argparse
import grp
import logging
import os
import pwd


def add_arguments():
    parser = argparse.ArgumentParser(
        description=('''Create a developer Docker container

This script adds a developer user to an existing docker image.
Caller can specify the parent docker image and user/group
combination of the newly created developer user.

The user id and user login name are determined by this program
from each other if either is specified in the command line options.

This program tries to resolve user account information by user authentication
database of the operating system if any of [user id; user login name] is
missing.

The user's id defaulted to the user who runs this program if neither user id
nor user login name is not specified in the command line.

The user's group defaulted to user's primary group if neither the group
name nor group id are specified in the command line.

If one of group id and group name is only specified in command line then the
missing associated data will be determined by the user authentication database
of the operating system.'''),
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '-u', '--userid', help="The inner developer user's identifier. "
        "See help of its default.", metavar='UserId', dest='user_id',
        default=None, required=False, type=int)
    parser.add_argument(
        '-l', '--login', help="The inner developer user's login name. "
        "See help of its default.", metavar='LoginName', dest='user_login',
        default=None, required=False)
    parser.add_argument(
        '-g', '--group', help="The inner developer's group id. Defaults to "
        "user's primary group.", metavar='GroupId', dest='group_id',
        default=None, required=False, type=int)
    parser.add_argument(
        '-n', '--group-name', help="The inner developer's group name. "
        "Defaults to user's primary group.", metavar='GroupName',
        dest='group_name', required=False)
    parser.add_argument(
        '-f', '--from', help="Parent Docker image specification. Defaults to "
        "'ubuntu:16.04'.", metavar='ParentImage', dest='parent_image',
        default="ubuntu:16.04", required=False)
    parser.add_argument(
        '-t', '--tag', help="Tag of the created image. Defaults to "
        "'dev-<FROM>'", metavar='ImageTag',
        dest='image_tag', default=None, required=False)
    parser.add_argument(
        '-s', '--shell', help="User's shell. Defaults to '/bin/bash'",
        metavar='Shell', dest='shell_program', default='/bin/bash',
        required=False)
    parser.add_argument(
        '-b', '--build-arg', action='append', dest='build_args', default=[],
        help='Add build args to the docker build command.', metavar='BuildArg',
        required=False)

    return parser


def is_user_in_docker_group(user_id):
    try:
        docker_gid = grp.getgrnam('docker').gr_gid
        return os.getgroups().index(docker_gid)
    except ValueError:
        return False


def resolve_user_name_by_id(user_id):
    return pwd.getpwuid(user_id).pw_name


def resolve_user_id_by_name(user_name):
    return pwd.getpwnam(user_name).pw_uid


def resolve_group_name_by_id(group_id):
    return grp.getgrgid(group_id).gr_name


def resolve_group_id_by_name(group_name):
    return grp.getgrnam(group_name).gr_gid


def resolve_primary_group_by_user_id(user_id):
    return pwd.getpwuid(user_id).pw_gid


def main():
    logging.basicConfig(level=logging.INFO)
    parser = add_arguments()
    args = parser.parse_args()

    if 0 == os.geteuid():  # This script is running as root
        if args.user_id is None and args.user_login is None:
            logging.error('Script is running as root. The user id and/or user '
                          'login name must be specified.')
            raise SystemExit

    user_name_switch = 'user_name='
    if args.user_id is None and args.user_login is None:
        user_id = os.getuid()
        user_name_switch += resolve_user_name_by_id(user_id)
    elif args.user_id is None and args.user_login is not None:
        user_id = resolve_user_id_by_name(args.user_login)
        user_name_switch += args.user_login
    elif args.user_id is not None and args.user_login is None:
        user_id = args.user_id
        user_name_switch += resolve_user_name_by_id(args.user_id)
    else:
        user_id = args.user_id
        user_name_switch += args.user_login

    user_id_switch = 'user_id=' + str(user_id)

    group_name_switch = 'group_name='
    if args.group_id is None and args.group_name is None:
        if 0 == os.getegid():
            group_id = resolve_primary_group_by_user_id(user_id)
        else:
            group_id = os.getgid()
        group_name_switch += resolve_group_name_by_id(group_id)
    elif args.group_id is None and args.group_name is not None:
        group_id = resolve_group_id_by_name(args.group_name)
        group_name_switch += args.group_name
    elif args.group_id is not None and args.group_name is None:
        group_id = args.group_id
        group_name_switch += resolve_group_name_by_id(group_id)
    else:
        group_id = args.group_id
        group_name_switch += args.group_name

    group_id_switch = 'group_id=' + str(group_id)

    if args.image_tag is None:
        image_tag = 'dev-' + args.parent_image
    else:
        image_tag = args.image_tag

    docker_context_dir = os.path.dirname(os.path.abspath(__file__))
    docker_file_name = os.path.join(docker_context_dir, 'Dockerfile')
    docker_file_switch = '--file=' + docker_file_name
    parent_image_switch = 'parent_image=' + args.parent_image

    if (0 == os.geteuid()) or \
            (os.environ.get('DOCKER_HOST') is not None) or \
            (is_user_in_docker_group(os.geteuid())):
        build_arguments = ['docker']
    else:
        build_arguments = ['sudo', 'docker']

    shell_program_switch = 'shell_program=' + args.shell_program

    build_arguments.extend(
        ['build',
         '--build-arg', user_id_switch, '--build-arg', group_id_switch,
         '--build-arg', user_name_switch, '--build-arg', group_name_switch,
         '--build-arg', parent_image_switch,
         '--build-arg', shell_program_switch])

    for arg in args.build_args:
        build_arguments.extend(['--build-arg', arg])

    build_arguments.extend(['--tag', image_tag, docker_file_switch,
                            docker_context_dir])
    os.execvp(build_arguments[0], build_arguments)


if __name__ == '__main__':
    main()
