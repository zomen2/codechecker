ARG UBUNTU_VERSION=20.04

FROM ubuntu:${UBUNTU_VERSION}

ARG UBUNTU_VERSION

LABEL com.ericsson.codechecker.ubuntu.version="${UBUNTU_VERSION}"

RUN apt-get update                                                             \
  && DEBIAN_FRONTEND=noninteractive apt-get install --yes locales

RUN sed --in-place --expression='s/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/'     \
    /etc/locale.gen                                                            \
  && dpkg-reconfigure --frontend=noninteractive locales                        \
  && update-locale LANG=en_US.UTF-8

ENV LANG en_US.UTF-8

RUN DEBIAN_FRONTEND=noninteractive apt-get install --yes                       \
    apt-utils                                                                  \
    ca-certificates                                                            \
    curl                                                                       \
    gpgv                                                                       \
    lsb-release

WORKDIR /root
COPY ./dbuild ./build
RUN chmod u+x                                                                  \
    ./build/install_dependencies.sh

RUN ./build/install_dependencies.sh

WORKDIR /tmp
