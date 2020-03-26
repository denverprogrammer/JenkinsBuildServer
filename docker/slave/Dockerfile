#Dockerfile

FROM ubuntu:18.04
 
ENV COMPOSE_VERSION 1.8.1
ENV USER_NAME "admin"
ENV USER_PASSWORD "admin"
ENV MASTER_URL "http://jenkins:8080"
ENV SLAVE_URL ""
ENV SLAVE_NAME ""
ENV SLAVE_SECRET ""
ENV SLAVE_EXECUTORS "1"
ENV SLAVE_LABELS "docker"
ENV SLAVE_WORKING_DIR ""
ENV CLEAN_WORKING_DIR "true"

RUN apt-get update && apt-get install -y \ 
    # Install dependencies in the agent container
    apt-transport-https \
    ca-certificates \
    openjdk-8-jre \
    curl \
    python3 \
    python3-pip \
    git && \ 
    pip3 install jenkins-webapi && \
    # Install docker agent container
    curl -fsSL https://get.docker.com -o get-docker.sh && \
    sh get-docker.sh && \
    rm get-docker.sh && \
    # Install docker-compose in the agent container
    curl -L https://github.com/docker/compose/releases/download/1.21.2/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose && \ 
    mkdir -p /home/jenkins && \
    mkdir -p /var/lib/jenkins

# Start-up script to attach the slave to the master
ADD scripts/slave.py /var/lib/jenkins/slave.py

WORKDIR /home/jenkins

CMD [ "python3", "-u", "/var/lib/jenkins/slave.py" ]
