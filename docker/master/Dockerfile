#Dockerfile

# Starting off with the Jenkins base Image
FROM jenkins/jenkins:lts-alpine

# Installing the plugins we need using the built-in install-plugins.sh script
RUN /usr/local/bin/install-plugins.sh \
    git \
    matrix-auth \
    workflow-aggregator \
    docker-workflow \
    blueocean \
    credentials-binding \
    ansicolor \
    authorize-project
 
# Skip the initial setup wizard
ENV JAVA_OPTS -Djenkins.install.runSetupWizard=false -Dhudson.security.csrf.DefaultCrumbIssuer.EXCLUDE_SESSION_ID=true

VOLUME /var/jenkins_home
