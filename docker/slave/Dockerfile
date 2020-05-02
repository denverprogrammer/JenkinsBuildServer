#Dockerfile

FROM alpine:latest
 
ENV COMPOSE_VERSION 1.8.1
ENV USER_NAME "admin"
ENV USER_PASSWORD "admin"
ENV MASTER_URL "http://jenkins:8080"
ENV SLAVE_URL ""
ENV SLAVE_NAME "jenkins-slave"
ENV SLAVE_SECRET ""
ENV SLAVE_EXECUTORS 5
ENV SLAVE_LABELS "PHP"
ENV SLAVE_WORKING_DIR "/home/jenkins"
ENV CLEAN_WORKING_DIR "true"

RUN apk update && apk add \ 
    ca-certificates \
    openjdk8-jre \
    curl \
    py3-pip \
    python3 \
    git \ 
    docker \
    openssh-client \
    docker-compose && \
    pip3 install jenkins-webapi && \
    mkdir -p /home/jenkins

WORKDIR /home/jenkins

CMD [ "python3", "-u", "/var/lib/jenkins/scripts/slave.py" ]
