# Set this parameter with --build-arg
ARG parent_image=ubuntu:20.04
FROM ${parent_image}

# Set these parameters with --build-arg
ARG user_id=2000
ARG group_id=2000
ARG user_name=developer
ARG group_name=developer
ARG shell_program=/bin/bash

USER root

COPY ./create_account.sh /tmp
RUN chmod u+x /tmp/create_account.sh
RUN /tmp/create_account.sh "${user_id}" "${user_name}" "${group_id}"           \
    "${group_name}" "${shell_program}"

USER ${user_name}
WORKDIR "/home/${user_name}"

CMD "${shell_program}"
