.PHONY: destroy build password push

# Common git commands
CURRENT_BRANCH = `git rev-parse --abbrev-ref HEAD`

# Brings down all containers.
destroy:
	docker-compose down --remove-orphans --volumes

# Builds all of the dev containers and starts the server.  
# In your browser go to http://localhost to view webpage.
build:
	docker-compose up --build -d

password:
	docker exec -c `tail /var/jenkins_home/secrets/initialAdminPassword`

# Common way to push to github.
push:
	git push -u origin ${CURRENT_BRANCH}