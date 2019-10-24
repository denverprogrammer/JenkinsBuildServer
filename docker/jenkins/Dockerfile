# Dockerfile
FROM docker:stable
ENV SWARM_CLIENT_VERSION="3.9"

RUN adduser -G root -D jenkins && \
    apk --update --no-cache add \
        openjdk8-jre \
        python \
        python-dev \
        musl-dev \
        libffi-dev \
        openssl-dev \
        py-pip \
        git \
        openssh \
        ca-certificates \
        openssl \
        make \
        gcc && \
    wget -O swarm-client.jar \
        -q https://repo.jenkins-ci.org/releases/org/jenkins-ci/plugins/swarm-client/${SWARM_CLIENT_VERSION}/swarm-client-${SWARM_CLIENT_VERSION}.jar \
        -P /home/jenkins/ && \
    pip install docker-compose

COPY docker/jenkins/jenkins-slave.sh /usr/local/bin/jenkins-slave.sh
RUN chmod +x /usr/local/bin/jenkins-slave.sh
ENTRYPOINT ["jenkins-slave.sh"]